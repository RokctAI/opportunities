# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import re
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent.parent.parent
TENDER_DIR = BASE_DIR / '03_tenders'
SOURCES_DIR = TENDER_DIR / 'sources'

def get_resilient_session():
    session = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.headers.update({'User-Agent': 'Mozilla/5.0 RokctAI-Resilient-Sync/1.0'})
    return session

def load_ocds_configs():
    configs = []
    if not SOURCES_DIR.exists(): return configs
    for source_file in SOURCES_DIR.glob('*.md'):
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(r'-\s+\*\*Is API\*\*:\s*true', content, re.I) and re.search(r'-\s+\*\*API Type\*\*:\s*OCDS', content, re.I):
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

def sync_tenders(config, days_back=7):
    session = get_resilient_session()
    PAGE_SIZE = 5000 
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Sync] {config['name']}...")
    
    params = {
        "PageNumber": 1, "PageSize": PAGE_SIZE, 
        "dateFrom": (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
        "dateTo": datetime.now().strftime('%Y-%m-%d')
    }

    try:
        response = session.get(config["url"], params=params, timeout=120)
        response.raise_for_status()
        releases = response.json().get('releases', [])
        
        # Deduplicate to latest
        latest = {}
        for r in releases:
            ocid = r.get('ocid')
            if ocid and (ocid not in latest or r.get('date', '') > latest[ocid].get('date', '')):
                latest[ocid] = r

        updates = 0
        for ocid, rel in latest.items():
            file_path = TENDER_DIR / f"{ocid}.md"
            if file_path.exists() and "Verification Status: VERIFIED" in open(file_path, 'r', encoding='utf-8').read():
                continue

            new_content = generate_md(rel, config['flag'], config['source_card'])
            
            # Robust comparison
            existing = ""
            if file_path.exists(): existing = open(file_path, 'r', encoding='utf-8').read()
            
            if [l.strip() for l in existing.splitlines() if l.strip()] != [l.strip() for l in new_content.splitlines() if l.strip()]:
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                updates += 1
        
        print(f"  [Status] Received {len(releases)} releases. Updated {updates} files.")
    except Exception as e:
        print(f"  [Error] {e}")

def generate_md(release, flag, source_ref):
    tender = release.get('tender', {})
    ocid = release.get('ocid')
    title = tender.get('title', 'Untitled')
    institution = tender.get('procuringEntity', {}).get('name', 'Unknown')
    published = release.get('date', '')[:10]
    closing = (tender.get('tenderPeriod', {}).get('endDate', '') or "").replace('T', ' ')[:16]
    
    raw_docs = tender.get('documents', [])
    processed_docs = sorted([(doc.get('title', 'Document'), doc.get('url', '#')) for doc in raw_docs], key=lambda x: (x[0], x[1]))
    docs_md = "".join([f"    - [{t}]({u})\n" for t, u in processed_docs]) or "    - No documents listed.\n"
    direct_link = processed_docs[0][1] if processed_docs else "#"

    return f"""# Tender Opportunity: {title}

## Quick Stats
- **Tender Number**: {ocid}
- **Institution**: {institution}
- **Source Card**: {source_ref}
- **Flag**: {flag}
- **Tender Type**: {tender.get('procurementMethodDetails', 'Tender')}
- **Province**: {tender.get('province', 'National')}
- **Date Published**: {published}
- **Closing Date**: {closing}
- **Place Required**: {tender.get('deliveryLocation', 'See Documents')}

## Detailed Description
### Category
{tender.get('category', 'General')}

### Tender Description
{tender.get('description', 'No description provided.')}

## Briefing Session
- **Is there a briefing session?**: {"Yes" if tender.get('briefingSession', {}).get('isSession') else "No"}
- **Is it compulsory?**: {"Yes" if tender.get('briefingSession', {}).get('compulsory') else "No"}
- **Briefing Date and Time**: {tender.get('briefingSession', {}).get('date', 'N/A').replace('T', ' ')[:16]}
- **Briefing Venue**: {tender.get('briefingSession', {}).get('venue', 'N/A')}

## Enquiries
- **Contact Person**: {tender.get('contactPerson', {}).get('name', 'N/A')}
- **Email**: {tender.get('contactPerson', {}).get('email', 'N/A')}

## Documents & Links
- **Direct Link**: {direct_link}
- **Tender Documents**:
{docs_md}

## Audit & Status
- **Status**: ACTIVE
- **Last Verified**: {datetime.now().strftime('%Y-%m-%d')}

## AI Checklist (Jules)
- [ ] Review Tender Documents | 1
- [ ] Prepare Initial Response | 3
"""

if __name__ == "__main__":
    configs = load_ocds_configs()
    for c in configs: sync_tenders(c)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] OCDS Sync Complete.")
