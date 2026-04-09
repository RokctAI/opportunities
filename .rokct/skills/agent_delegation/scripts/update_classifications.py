# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
import pandas as pd
from pathlib import Path

def update_classifications():
    """Generates classification reference files for recipients."""
    print("🏷️ Updating Registry Classifications...")

    config_dir = Path('.rokct/config/classifications')
    config_dir.mkdir(parents=True, exist_ok=True)

    # 1. EQUITY
    equity_dir = Path('01_equity')
    industries = set()
    territories = set()
    for f in equity_dir.glob('*.md'):
        if f.name in ['registry_audit_log.md', 'global_audit_log.md']: continue
        with open(f, 'r') as content:
            lines = content.readlines()
            for line in lines:
                if '|' in line and ':' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) > 8:
                        territories.add(parts[7])
                        industries.add(parts[8])

    save_list(config_dir / 'equity_industries.txt', industries)
    save_list(config_dir / 'equity_territories.txt', territories)

    # 2. GRANTS
    grants_dir = Path('02_grants')
    focus_areas = set()
    for f in grants_dir.glob('*.md'):
        if f.name == 'template.md': continue
        with open(f, 'r') as content:
            match = re.search(r'-\s+\*\*Focus Area\*\*:\s*(.+)$', content.read(), re.MULTILINE)
            if match:
                areas = [a.strip() for a in match.group(1).split(',')]
                focus_areas.update(areas)

    save_list(config_dir / 'grants_focus_areas.txt', focus_areas)

    # 3. TENDERS
    tenders_dir = Path('03_tenders')
    categories = set()
    institutions = set()
    types = set()
    for f in tenders_dir.glob('*.md'):
        if f.name == 'template.md': continue
        with open(f, 'r') as content:
            text = content.read()
            cat_match = re.search(r'### Category\s*\n\s*(.+)', text)
            if cat_match: categories.add(cat_match.group(1).strip())

            inst_match = re.search(r'-\s+\*\*Institution\*\*:\s*(.+)$', text, re.MULTILINE)
            if inst_match: institutions.add(inst_match.group(1).strip())

            type_match = re.search(r'-\s+\*\*Tender Type\*\*:\s*(.+)$', text, re.MULTILINE)
            if type_match: types.add(type_match.group(1).strip())

    save_list(config_dir / 'tender_categories.txt', categories)
    save_list(config_dir / 'tender_institutions.txt', institutions)
    save_list(config_dir / 'tender_types.txt', types)

def save_list(path, items):
    items = sorted([i for i in items if i and i != "N/A" and "[" not in i])
    with open(path, 'w') as f:
        f.write('\n'.join(items))
    print(f"✅ Saved {path.name}")

if __name__ == "__main__":
    update_classifications()
