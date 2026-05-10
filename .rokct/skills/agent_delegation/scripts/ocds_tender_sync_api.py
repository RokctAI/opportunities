# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import re
import json
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
    """Creates a requests session with high resilience."""
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
            is_api = re.search(r'-\s+\*\*Is API\*\*:\s*true', content, re.IGNORECASE)
            is_ocds = re.search(r'-\s+\*\*API Type\*\*:\s*OCDS', content, re.IGNORECASE)
            
            if is_api and is_ocds:
                u_match = re.search(r'-\s+\*\*URL\*\*:\s*(https?://[^\s\n]+)', content)
                f_match = re.search(r'-\s+\*\*Flag\*\*:\s*([A-Z]{2})', content)
                if u_match and f_match:
                    configs.append({
                        "name": source_file.stem,
                        "source_card": f"sources/{source_file.name}",
                        "url": u_match.group(1).strip(),
                        "flag": f_match.group(1).strip()
                    })
    return configs

def fetch_and_sync_tenders(source_config, days_back=7):
    """Fetches tenders using Ultra-Batching and Latest-First Deduplication."""
    base_url = source_config["url"]
    flag = source_config["flag"]
    source_ref = source_config["source_card"]
    session = get_resilient_session()
    
    PAGE_SIZE = 5000 
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Sync] Fetching {source_config['name']} (PageSize: {PAGE_SIZE})...")
    
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    params = {"PageNumber": 1, "PageSize": PAGE_SIZE, "dateFrom": date_from, "dateTo": date_to}

    try:
        response = session.get(base_url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
        releases = data.get('releases', [])
        
        if not releases:
            print("  [Info] No releases found.")
            return 0

        # --- DEDUPLICATION: Keep only the latest release for each OCID ---
        # OCDS releases are usually ordered by date descending, but we ensure it.
        latest_releases = {}
        for release in releases:
            ocid = release.get('ocid')
            if not ocid: continue
            
            # If multiple releases exist for the same OCID, keep the one with the latest 'date'
            rel_date = release.get('date', '')
            if ocid not in latest_releases or rel_date > latest_releases[ocid].get('date', ''):
                latest_releases[ocid] = release

        updates = 0
        print(f"  [Integrity] Found {len(releases)} releases ({len(latest_releases)} unique tenders). Checking for changes...")

        for ocid, release in latest_releases.items():
            file_path = TENDER_DIR / f"{ocid}.md"
            
            existing_content = ""
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                if "Verification Status: VERIFIED" in existing_content:
                    continue

            new_content = generate_markdown_from_ocds(release, flag, source_ref)
            
            # ROBUST COMPARISON: Ignore line endings and trailing whitespace
            existing_lines = [line.strip() for line in existing_content.splitlines() if line.strip()]
            new_lines = [line.strip() for line in new_content.splitlines() if line.strip()]
            
            if existing_lines != new_lines:
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                updates += 1
        
        print(f"  [Status] Done. {updates} files genuinely updated.")
        return len(latest_releases)

    except Exception as e:
        print(f"  [Error] Sync failed: {e}")
        return 0

def generate_markdown_from_ocds(release, flag, source_ref):
    """Maps OCDS JSON fields with Deterministic Stability."""
    tender = release.get('tender', {})
    ocid = release.get('ocid')
    
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
    
    # Documents - STABLE SORTING
    raw_docs = tender.get('documents', [])
    processed_docs = sorted(
        [(doc.get('title', 'Document'), doc.get('url', '#')) for doc in raw_docs],
        key=lambda x: (x[0], x[1])
    )
    
    docs_md = "".join([f"    - [{t}]({u})\n" for t, u in processed_docs])
    if not docs_md: docs_md = "    - No documents listed in API.\n"

    # Direct Link Determinism
    direct_link = "https://www.etenders.gov.za/Home/opportunities?id=1"
    if processed_docs:
        direct_link = processed_docs[0][1]

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
        for config in configs:
            fetch_and_sync_tenders(config)
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] OCDS Sync Complete.")