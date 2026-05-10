import os
import re
from pathlib import Path

TENDER_DIR = Path('03_tenders')

def backfill_sources():
    print("Backfilling Source Card metadata for existing tenders...")
    count = 0
    
    for md_file in TENDER_DIR.glob('*.md'):
        if md_file.name in ['template.md', 'registry_audit_log.md']:
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Determine source based on filename
        source_ref = None
        if md_file.name.startswith('ocds-'):
            source_ref = "sources/etendersZA.md"
        elif md_file.name.startswith('musina-'):
            source_ref = "sources/musinaZA.md"
            
        if source_ref and "Source Card" not in content:
            # Inject after Institution
            new_line = f"- **Source Card**: {source_ref}\n"
            content = re.sub(r'(-\s+\*\*Institution\*\*:[^\n]+\n)', r'\1' + new_line, content)
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            
    print(f"✅ Backfilled {count} cards with Source Card metadata.")

if __name__ == "__main__":
    backfill_sources()
