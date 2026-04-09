# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path

# --- CONFIGURATION ---
BASE_URL = "https://ocds-api.etenders.gov.za/api/OCDSReleases"
TENDER_DIR = Path('03_tenders')
GRANT_DIR = Path('02_grants')
TEMPLATE_PATH = TENDER_DIR / 'template.md'

def fetch_and_sync_tenders(page_limit=5, days_back=7):
    """Fetches tenders from API and updates local registry."""
    print(f"🚀 Starting Live OCDS Tender Sync (Last {days_back} days)...")
    
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
        print(f"📄 Fetching page {params['PageNumber']}...")
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            releases = data.get('releases', [])
            if not releases:
                print("🏁 No more releases found.")
                break
                
            for release in releases:
                ocid = release.get('ocid')
                if not ocid: continue
                
                # RULE: OCID-Stable Filenames
                filename = f"{ocid}.md"
                file_path = TENDER_DIR / filename
                
                markdown_content = generate_markdown_from_ocds(release)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                count += 1
                
            # Check for next page
            if not data.get('links', {}).get('next'):
                break
            params["PageNumber"] += 1
            
        except Exception as e:
            print(f"❌ Error fetching page {params['PageNumber']}: {e}")
            break

    print(f"✅ Sync complete. Processed {count} tenders.")
    purge_expired_tenders()
    purge_expired_grants()

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
    # Use first document URL as applying link if available, fallback to portal
    docs = tender.get('documents', [])
    if docs and docs[0].get('url'):
        applying_link = docs[0].get('url')
    else:
        applying_link = "https://www.etenders.gov.za/Home/opportunities?id=1"

    # Assemble Markdown
    md = f"""# Tender Opportunity: {title}

## Quick Stats
- **Tender Number**: {ocid}
- **Institution**: {institution}
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
- **Applying Link**: {applying_link}
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
    TENDER_DIR.mkdir(parents=True, exist_ok=True)
    fetch_and_sync_tenders()