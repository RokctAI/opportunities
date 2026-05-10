# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
from datetime import datetime
from pathlib import Path
import json

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent.parent.parent
TENDER_DIR = BASE_DIR / '03_tenders'
GRANT_DIR = BASE_DIR / '02_grants'
QUEUE_DIR = BASE_DIR / '.rokct' / 'agent' / 'queue'

def purge_expired():
    """Removes tenders and grants that have passed their deadlines."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Maintenance] Purging expired entries...")
    now = datetime.now()
    count = 0
    
    # Purge Tenders
    for f in TENDER_DIR.glob('*.md'):
        if f.name in ['template.md', 'registry_audit_log.md'] or f.name.startswith('registry_'):
            continue
        with open(f, 'r', encoding='utf-8') as content:
            match = re.search(r'-\s+\*\*Closing Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content.read())
            if match and datetime.strptime(match.group(1), '%Y-%m-%d') < now:
                os.remove(f)
                count += 1
    
    print(f"  [Status] Purged {count} expired items.")

def queue_ai():
    """Queues new tenders for AI analysis."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    new_tenders = []
    
    for f in TENDER_DIR.glob('ocds-*.md'):
        with open(f, 'r', encoding='utf-8') as content:
            text = content.read()
            if "Status: ACTIVE" in text and "[e.g.," in text:
                new_tenders.append(f.name)

    if new_tenders:
        task = {
            "title": f"Tender Analysis: {datetime.now().strftime('%Y-%m-%d')}",
            "files": new_tenders[:20],
            "instruction": "Verify document requirements and update AI Analysis section."
        }
        with open(QUEUE_DIR / f"ai_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(task, f, indent=2)
        print(f"  [Status] Queued AI task for {len(new_tenders)} items.")

if __name__ == "__main__":
    purge_expired()
    queue_ai()
