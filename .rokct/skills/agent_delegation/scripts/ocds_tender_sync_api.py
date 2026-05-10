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
    """Creates a requests session with high resilience for flaky government APIs."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def load_ocds_api_configs():
    """Finds all markdown cards in sources/ marked as Is API: true and API Type: OCDS."""
    configs = []
    if not SOURCES_DIR.exists(): return configs

    for source_file in SOURCES_DIR.glob('*.md'):
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Is API: true' in content and 'API Type: OCDS' in content:
                config = {
                    "name": source_file.stem,
                    "source_card": f"sources/{source_file.name}",
                    "url": re.search(r'-\s+\*\*URL\*\*:\s*(https?://[^\s\n]+)', content).group(1).strip(),
                    "flag": re.search(r'-\s+\*\*Flag\*\*:\s*([A-Z]{2})', content).group(1).strip()
                }
                configs.append(config)
    return configs

def fetch_and_sync_tenders(source_config, page_limit=20, days_back=7):
    """Fetches tenders from an OCDS API with persistence logic."""
    base_url = source_config["url"]
    flag = source_config["flag"]
    source_ref = source_config["source_card"]
    session = get_resilient_session()
    
    print(f"  [Pass] Fetching {source_config['name']} ({flag})...")
    
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    params = {"PageNumber": 1, "PageSize": 100, "dateFrom": date_from, "dateTo": date_to}

    updates = 0
    unique_ids = set()

    while params["PageNumber"] <= page_limit:
        try:
            response = session.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            releases = data.get('releases', [])
            if not releases: break
                
            for release in releases:
                ocid = release.get('ocid')
                if not ocid: continue
                
                file_path = TENDER_DIR / f"{ocid}.md"
                existing_content = ""
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    
                    if "Verification Status: VERIFIED" in existing_content:
                        continue

                new_content = generate_markdown_from_ocds(release, flag, source_ref, existing_content)
                
                # Only write if content actually changed (to keep Git history clean)
                if new_content.strip() != existing_content.strip():
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updates += 1
                    unique_ids.add(ocid)
                
            if not data.get('links', {}).get('next'): break
            params["PageNumber"] += 1
            
        except Exception as e:
            print(f"    [Error] Page {params['PageNumber']}: {e}")
            break

    return updates

def generate_markdown_from_ocds(release, flag, source_ref, existing_content=""):
    """Maps OCDS JSON fields and MERGES with existing documents to prevent data loss."""
    tender = release.get('tender', {})
    ocid = release.get('ocid')
    
    # Basic Metadata
    title = tender.get('title', 'Untitled Opportunity')
    institution = tender.get('procuringEntity', {}).get('name', 'Unknown')
    t_type = tender.get('procurementMethodDetails', tender.get('mainProcurementCategory', 'Tender'))
    province = tender.get('province', 'National')
    published = release.get('date', '')[:10]
    closing = (tender.get('tenderPeriod', {}).get('endDate', '') or "").replace('T', ' ')[:16]
    location = tender.get('deliveryLocation', 'See Documents')
    category = tender.get('category', 'General')
    description = tender.get('description', 'No description provided.')

    # Briefing
    briefing = tender.get('briefingSession', {})
    has_briefing = "Yes" if briefing.get('isSession') else "No"
    compulsory = "Yes" if briefing.get('compulsory') else "No"
    b_date = briefing.get('date', 'N/A').replace('T', ' ')[:16] if briefing.get('date') else "N/A"
    b_venue = briefing.get('venue', 'N/A')
    
    # Documents - MERGE LOGIC
    existing_docs = set(re.findall(r'\[(.*?)\]\((.*?)\)', existing_content))
    new_docs = set()
    for doc in tender.get('documents', []):
        new_docs.add((doc.get('title', 'Document'), doc.get('url', '#')))
    
    all_docs = sorted(list(existing_docs.union(new_docs)))
    docs_md = "".join([f"    - [{t}]({u})\n" for t, u in all_docs])
    if not docs_md: docs_md = "    - No documents listed in API.\n"

    # Direct Link Logic (prefer new, fallback to existing)
    direct_link = "https://www.etenders.gov.za/Home/opportunities?id=1"
    if all_docs: direct_link = all_docs[0][1]

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

## Briefing Session
- **Is there a briefing session?**: {has_briefing}
- **Is it compulsory?**: {compulsory}
- **Briefing Date and Time**: {b_date}
- **Briefing Venue**: {b_venue}

## Enquiries
- **Contact Person**: {tender.get('contactPerson', {}).get('name', 'N/A')}
- **Email**: {tender.get('contactPerson', {}).get('email', 'N/A')}
- **Telephone**: {tender.get('contactPerson', {}).get('telephoneNumber', 'N/A')}

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
    configs = load_ocds_api_configs()
    
    if not configs:
        print("No API sources found.")
    else:
        # TRIPLE-PASS SWEEP for flaky API resilience
        for pass_num in range(1, 4):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] --- SWEEP PASS {pass_num}/3 ---")
            total = 0
            for config in configs:
                total += fetch_and_sync_tenders(config)
            print(f"  [Pass {pass_num}] Updated {total} files.")
            if pass_num < 3: time.sleep(5) # Cooldown
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] OCDS Sync Complete.")