# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import re
import difflib
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Robust environment loading from .env/production.env."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_path = os.path.join(project_root, ".env", "production.env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
        # Aggressive manual recovery if standard loader misses export syntax
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.replace("export ", "").strip().split("=", 1)
                    if not os.environ.get(key.strip()):
                        os.environ[key.strip()] = val.strip("'\" ")
    else:
        load_dotenv()

# --- CONFIGURATION ---
TENDER_DIR = Path('03_tenders')
GRANT_DIR = Path('02_grants')
TEMPLATE_PATH = TENDER_DIR / 'template.md'
SOURCES_DIR = TENDER_DIR / 'sources'

def load_api_source_configs():
    """Finds all markdown cards in sources/ marked as Is API: true."""
    configs = []
    for source_file in SOURCES_DIR.glob('*.md'):
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            is_api = re.search(r'-\s+\*\*Is API\*\*:\s*true', content, re.IGNORECASE)
            if is_api:
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

def fetch_and_sync_tenders(source_config, page_limit=5, days_back=7):
    """Fetches tenders from a specific OCDS API and updates local registry."""
    base_url = source_config["url"]
    flag = source_config["flag"]
    source_ref = source_config["source_card"]
    
    print(f"🚀 Syncing {source_config['name']} ({flag}) from {base_url}...")
    
    # Dynamic Date Range
    now = datetime.now()
    date_to = now.strftime('%Y-%m-%d')
    date_from = (now - timedelta(days=days_back)).strftime('%Y-%m-%d')

    params = {
        "PageNumber": 1,
        "PageSize": 50,
        "dateFrom": date_from,
        "dateTo": date_to
    }

    count = 0
    while params["PageNumber"] <= page_limit:
        print(f"  📄 Page {params['PageNumber']}...")
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            releases = data.get('releases', [])
            if not releases: break
                
            for release in releases:
                ocid = release.get('ocid')
                if not ocid: continue
                
                tender_data = release.get('tender', {})
                title = tender_data.get('title', 'Untitled')

                # DUPLICATION CHECK
                filename = f"{ocid}.md"
                file_path = TENDER_DIR / filename
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if "Verification Status: VERIFIED" in f.read() or "Status: VERIFIED" in f.read():
                            continue
                
                markdown_content = generate_markdown_from_ocds(release, flag, source_ref)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                count += 1
                
            if not data.get('links', {}).get('next'): break
            params["PageNumber"] += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            break

    print(f"  ✅ Processed {count} tenders.")
    return count

def run_orchestrator():
    """Orchestrates sync for all API sources."""
    load_environment()
    TENDER_DIR.mkdir(parents=True, exist_ok=True)
    
    api_configs = load_api_source_configs()
    total_new = 0
    
    if not api_configs:
        print("ℹ️ No API sources found in sources/*.md")
    
    for config in api_configs:
        total_new += fetch_and_sync_tenders(config)
        
    print(f"🏁 Total new tenders added: {total_new}")
    purge_expired_tenders()
    purge_expired_grants()
    queue_ai_enrichment()

def queue_ai_enrichment():
    """Queues a delegation task for Jules to analyze new tenders."""
    queue_dir = Path('.rokct/agent/queue')
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    # We only analyze new unverified tenders
    new_tenders = []
    for f in TENDER_DIR.glob('ocds-*.md'):
        with open(f, 'r') as content:
            text = content.read()
            if "Verification Status: IN_PROGRESS" in text or "Status: ACTIVE" in text:
                if "AI Analysis: Compliance & Requirements" in text and "[e.g.," in text:
                    new_tenders.append(f.name)

    if not new_tenders: return

    task = {
        "title": f"Tender Analysis: {datetime.now().strftime('%Y-%m-%d')}",
        "repo": "opportunities",
        "prompt": f"TASK: Deep Document Analysis for {len(new_tenders)} new tenders.\n\n"
                  f"FILES: {', '.join(new_tenders[:10])}\n\n"
                  f"INSTRUCTIONS:\n"
                  f"1) For each file, visit the 'Direct Link' (document URL).\n"
                  f"2) Extract: Mandatory Requirements (B-BBEE, Tax, etc.), Key Deliverables, and Technical Specs.\n"
                  f"3) Update the 'AI Analysis' section of each markdown card.\n"
                  f"4) If documents are missing or link is dead, mark as 'Status: BROKEN'.\n"
                  f"5) Once done, change 'Verification Status' to 'VERIFIED'.",
        "automation_mode": "AUTO_CREATE_PR"
    }
    
    with open(queue_dir / f"tender_analysis_{datetime.now().strftime('%s')}.json", 'w') as f:
        import json
        json.dump(task, f, indent=2)
    print(f"🤖 Queued AI enrichment task for {len(new_tenders)} tenders.")

def generate_markdown_from_ocds(release):
    """Maps OCDS JSON fields to Monorepo Template."""
    tender = release.get('tender', {})
    ocid = release.get('ocid')
    
    # 1. Basic Metadata
    title = tender.get('title', 'Untitled Opportunity')
    institution = tender.get('procuringEntity', {}).get('name', 'Unknown')
    t_type = tender.get('mainProcurementCategory', 'Tender')
    province = tender.get('province', 'National')
    published = release.get('date', '')[:10] # YYYY-MM-DD
    closing = tender.get('tenderPeriod', {}).get('endDate', '')
    if closing and 'T' in closing:
        closing = closing.replace('T', ' ')[:16] # YYYY-MM-DD HH:MM
    
    location = tender.get('deliveryLocation', 'See Documents')
    category = tender.get('category', 'General')
    description = tender.get('description', 'No description provided.')
    conditions = tender.get('specialConditions', 'N/A')
    
    # Use procurementMethodDetails as the "Type" for classification
    t_type = tender.get('procurementMethodDetails', t_type)

    # 2. Briefing Session
    briefing = tender.get('briefingSession', {})
    has_briefing = "Yes" if briefing.get('isSession') else "No"
    compulsory = "Yes" if briefing.get('compulsory') else "No"
    b_date = briefing.get('date', 'N/A')
    if b_date and 'T' in b_date and b_date != '0001-01-01T00:00:00Z':
        b_date = b_date.replace('T', ' ')[:16]
    else:
        b_date = "N/A"
    b_venue = briefing.get('venue', 'N/A')
    
    # 3. Contacts
    contact = tender.get('contactPerson', {})
    c_name = contact.get('name', 'N/A')
    c_email = contact.get('email', 'N/A')
    c_tel = contact.get('telephoneNumber', 'N/A')
    
    # 4. Documents
    docs_md = ""
    for doc in tender.get('documents', []):
        d_title = doc.get('title', 'Document')
        d_url = doc.get('url', '#')
        docs_md += f"    - [{d_title}]({d_url})\n"
    
    if not docs_md:
        docs_md = "    - No documents listed in API.\n"

    # 5. Direct Link Logic
    # Use first document URL as direct link if available, fallback to portal
    docs = tender.get('documents', [])
    if docs and docs[0].get('url'):
        direct_link = docs[0].get('url')
    else:
        direct_link = "https://www.etenders.gov.za/Home/opportunities?id=1"

    # Assemble Markdown
    md = f"""# Tender Opportunity: {title}

## Quick Stats
- **Tender Number**: {ocid}
- **Institution**: {institution}
- **Source Card**: {SOURCE_CARD_REF}
- **Flag**: {REGION_FLAG}
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

def purge_expired_tenders():
    """Removes tender files that have passed their closing date."""
    print("Running self-cleaning audit for expired tenders...")
    now = datetime.now()
    
    for md_file in TENDER_DIR.glob('*.md'):
        if md_file.name in ['template.md', 'registry_audit_log.md']:
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract closing date (YYYY-MM-DD)
        match = re.search(r'-\s+\*\*Closing Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            closing_date_str = match.group(1)
            try:
                closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d')
                if closing_date < now:
                    print(f"🔥 Deleting expired tender: {md_file.name} (Closed: {closing_date_str})")
                    os.remove(md_file)
            except Exception as e:
                print(f"⚠️ Could not parse date for {md_file.name}: {e}")

def purge_expired_grants():
    """Removes grant files from 02_grants that have passed their deadline."""
    print("Running self-cleaning audit for expired grants...")
    now = datetime.now()
    count = 0
    
    if not GRANT_DIR.exists():
        return

    for md_file in GRANT_DIR.glob('*.md'):
        if md_file.name == 'template.md':
            continue
            
        # Format: YYYY-MM-DD_Grant_Name.md
        match = re.match(r'^(\d{4}-\d{2}-\d{2})_', md_file.name)
        if match:
            deadline_str = match.group(1)
            try:
                deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d')
                if deadline_date < now:
                    print(f"🔥 Deleting expired grant: {md_file.name} (Deadline: {deadline_str})")
                    os.remove(md_file)
                    count += 1
            except Exception as e:
                print(f"⚠️ Could not parse date for {md_file.name}: {e}")
                
    print(f"✅ Grant cleanup complete. Removed {count} expired grants.")

if __name__ == "__main__":
    load_environment()
    TENDER_DIR.mkdir(parents=True, exist_ok=True)
    fetch_and_sync_tenders()