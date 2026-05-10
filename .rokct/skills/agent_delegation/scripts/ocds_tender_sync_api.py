# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import re
import difflib
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def load_environment():
    """Robust environment loading from .env/production.env."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_path = os.path.join(project_root, ".env", "production.env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()

# --- CONFIGURATION ---
TENDER_DIR = Path('03_tenders')
SOURCES_DIR = TENDER_DIR / 'sources'

def get_resilient_session():
    """Creates a requests session with retry logic and SSL tolerance."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5, # Increased retries
        backoff_factor=2, # Slower backoff
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def load_ocds_api_configs():
    """Finds all markdown cards in sources/ marked as Is API: true and API Type: OCDS."""
    configs = []
    if not SOURCES_DIR.exists():
        print(f"Sources directory missing: {SOURCES_DIR}")
        return configs

    for source_file in SOURCES_DIR.glob('*.md'):
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            is_api = re.search(r'-\s+\*\*Is API\*\*:\s*true', content, re.IGNORECASE)
            is_ocds = re.search(r'-\s+\*\*API Type\*\*:\s*OCDS', content, re.IGNORECASE)
            
            if is_api and is_ocds:
                config = {
                    "name": source_file.stem,
                    "source_card": f"sources/{source_file.name}",
                    "url": None,
                    "flag": "UNKNOWN"
                }
                u_match = re.search(r'-\s+\*\*URL\*\*:\s*(https?://[^\s\n]+)', content)
                if u_match: config["url"] = u_match.group(1).strip()
                
                f_match = re.search(r'-\s+\*\*Flag\*\*:\s*([A-Z]{2})', content)
                if f_match: config["flag"] = f_match.group(1).strip()
                
                if config["url"]:
                    configs.append(config)
    return configs

def fetch_and_sync_tenders(source_config, page_limit=20, days_back=7):
    """Fetches ALL tenders from an OCDS API for the given date range."""
    base_url = source_config["url"]
    flag = source_config["flag"]
    source_ref = source_config["source_card"]
    
    session = get_resilient_session()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Sync] Starting {source_config['name']} ({flag})...")
    
    now = datetime.now()
    date_to = now.strftime('%Y-%m-%d')
    date_from = (now - timedelta(days=days_back)).strftime('%Y-%m-%d')

    params = {
        "PageNumber": 1,
        "PageSize": 100, # Increased page size for efficiency
        "dateFrom": date_from,
        "dateTo": date_to
    }

    releases_processed = 0
    unique_tenders_updated = 0
    unique_ids = set()

    while params["PageNumber"] <= page_limit:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Fetching Page {params['PageNumber']}...")
        try:
            response = session.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            releases = data.get('releases', [])
            if not releases:
                print("  [Info] Reached end of data stream.")
                break
                
            for release in releases:
                ocid = release.get('ocid')
                if not ocid: continue
                
                file_path = TENDER_DIR / f"{ocid}.md"
                is_new = not file_path.exists()
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # FLAG RECOVERY
                        if f"- **Flag**: {flag}" not in content and "- **Flag**:" not in content:
                            new_line = f"- **Flag**: {flag}\n"
                            content = re.sub(r'(-\s+\*\*Source Card\*\*:[^\n]+\n)', r'\1' + new_line, content)
                            with open(file_path, 'w', encoding='utf-8') as fw:
                                fw.write(content)

                        if "Verification Status: VERIFIED" in content or "Status: VERIFIED" in content:
                            continue
                
                markdown_content = generate_markdown_from_ocds(release, flag, source_ref)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                releases_processed += 1
                if ocid not in unique_ids:
                    unique_tenders_updated += 1
                    unique_ids.add(ocid)
                
            # OCDS APIs often use 'links' for pagination
            if not data.get('links', {}).get('next'): 
                print("  [Info] No 'next' link found. Sync complete.")
                break
            
            params["PageNumber"] += 1
            
        except Exception as e:
            print(f"  [Error] Failed at page {params['PageNumber']}: {e}")
            break

    print(f"  [Status] {source_config['name']} Done: {releases_processed} releases handled. {unique_tenders_updated} tenders synced.")
    return unique_tenders_updated

def generate_markdown_from_ocds(release, flag, source_ref):
    """Maps OCDS JSON fields to Monorepo Template."""
    tender = release.get('tender', {})
    ocid = release.get('ocid')
    
    title = tender.get('title', 'Untitled Opportunity')
    institution = tender.get('procuringEntity', {}).get('name', 'Unknown')
    t_type = tender.get('procurementMethodDetails', tender.get('mainProcurementCategory', 'Tender'))
    province = tender.get('province', 'National')
    published = release.get('date', '')[:10]
    
    closing = tender.get('tenderPeriod', {}).get('endDate', '')
    if closing and 'T' in closing:
        closing = closing.replace('T', ' ')[:16]
    
    location = tender.get('deliveryLocation', 'See Documents')
    category = tender.get('category', 'General')
    description = tender.get('description', 'No description provided.')
    conditions = tender.get('specialConditions', 'N/A')

    # Briefing
    briefing = tender.get('briefingSession', {})
    has_briefing = "Yes" if briefing.get('isSession') else "No"
    compulsory = "Yes" if briefing.get('compulsory') else "No"
    b_date = briefing.get('date', 'N/A').replace('T', ' ')[:16] if briefing.get('date') else "N/A"
    b_venue = briefing.get('venue', 'N/A')
    
    # Contacts
    contact = tender.get('contactPerson', {})
    c_name = contact.get('name', 'N/A')
    c_email = contact.get('email', 'N/A')
    c_tel = contact.get('telephoneNumber', 'N/A')
    
    # Documents
    docs_md = ""
    direct_link = "https://www.etenders.gov.za/Home/opportunities?id=1"
    docs = tender.get('documents', [])
    for doc in docs:
        d_title = doc.get('title', 'Document')
        d_url = doc.get('url', '#')
        docs_md += f"    - [{d_title}]({d_url})\n"
        if not direct_link or "etenders.gov.za" in direct_link:
            direct_link = d_url

    if not docs_md: docs_md = "    - No documents listed in API.\n"

    # Assemble Markdown
    md = f"""# Tender Opportunity: {title}

## Quick Stats
- **Tender Number**: {ocid}
- **Institution**: {institution}
- **Source Card**: {source_ref}
- **Flag**: {flag}
- **Tender Type**: {t_type}
- **Province**: {province}
- **Date Published**: {published}
- **Closing Date**: {closing}
- **Place Required**: {location}

## Detailed Description
### Category
{category}

### Tender Description
{description}

### Special Conditions
{conditions}

## Briefing Session
- **Is there a briefing session?**: {has_briefing}
- **Is it compulsory?**: {compulsory}
- **Briefing Date and Time**: {b_date}
- **Briefing Venue**: {b_venue}

## Enquiries
- **Contact Person**: {c_name}
- **Email**: {c_email}
- **Telephone**: {c_tel}

## Documents & Links
- **Direct Link**: {direct_link}
- **Tender Documents**:
{docs_md}

## Audit & Status
- **Status**: ACTIVE
- **Last Verified**: {datetime.now().strftime('%Y-%m-%d')}

## AI Checklist (Jules)
<!-- This section is populated by Jules during enrichment. Format: - [ ] Subject | Due Date Offset (Days) -->
- [ ] Review Tender Documents | 1
- [ ] Prepare Initial Response | 3
"""
    return md

if __name__ == "__main__":
    load_environment()
    TENDER_DIR.mkdir(parents=True, exist_ok=True)
    
    api_configs = load_ocds_api_configs()
    total_unique = 0
    
    if not api_configs:
        print("No API sources found.")
    else:
        for config in api_configs:
            total_unique += fetch_and_sync_tenders(config)
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] OCDS Sync complete. Unique tenders in registry: {total_unique}")