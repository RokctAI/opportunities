# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
TENDER_DIR = Path('03_tenders')
GRANT_DIR = Path('02_grants')
QUEUE_DIR = Path('.rokct/agent/queue')

def purge_expired_tenders():
    """Removes tender files that have passed their closing date."""
    print("🧹 Running self-cleaning audit for expired tenders...")
    now = datetime.now()
    count = 0
    
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
                    count += 1
            except Exception as e:
                print(f"⚠️ Could not parse date for {md_file.name}: {e}")
    
    print(f"✅ Tender cleanup complete. Removed {count} expired tenders.")

def purge_expired_grants():
    """Removes grant files from 02_grants that have passed their deadline."""
    print("🧹 Running self-cleaning audit for expired grants...")
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

def queue_ai_enrichment():
    """Queues a delegation task for Jules to analyze new tenders."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    
    # We only analyze new unverified tenders
    new_tenders = []
    for f in TENDER_DIR.glob('ocds-*.md'):
        with open(f, 'r', encoding='utf-8') as content:
            text = content.read()
            if ("Verification Status: IN_PROGRESS" in text or "Status: ACTIVE" in text) and "[e.g.," in text:
                new_tenders.append(f.name)

    if not new_tenders:
        print("ℹ️ No new tenders requiring AI enrichment.")
        return

    task = {
        "title": f"Tender Analysis: {datetime.now().strftime('%Y-%m-%d')}",
        "repo": "opportunities",
        "prompt": f"TASK: Deep Document Analysis for {len(new_tenders)} new tenders.\n\n"
                  f"FILES: {', '.join(new_tenders[:10])}\n\n"
                  f"INSTRUCTIONS:\n"
                  f"1) For each file, visit the 'Direct Link' (document URL).\n"
                  f"2) Extract: Mandatory Requirements, Key Deliverables, and Technical Specs.\n"
                  f"3) Update the 'AI Analysis' section of each markdown card.\n"
                  f"4) Once done, change 'Verification Status' to 'VERIFIED'.",
        "automation_mode": "AUTO_CREATE_PR"
    }
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(QUEUE_DIR / f"tender_analysis_{timestamp}.json", 'w') as f:
        import json
        json.dump(task, f, indent=2)
    print(f"🤖 Queued AI enrichment task for {len(new_tenders)} tenders.")

if __name__ == "__main__":
    purge_expired_tenders()
    purge_expired_grants()
    queue_ai_enrichment()
