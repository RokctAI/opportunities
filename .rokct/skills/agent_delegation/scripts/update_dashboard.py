# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta

def update_readme_stats():
    """Calculates registry stats and updates the main README.md and generates data for GitHub Pages."""
    print("📊 Updating Registry Dashboard & Data...")
    
    project_root = Path(__file__).parent.parent.parent.parent.parent
    readme_path = project_root / 'README.md'
    docs_dir = project_root / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # 1. Calculate Stats and Gather Data
    stats = {
        'Equity': {'total': 0, 'verified': 0, 'new': 0},
        'Grants': {'total': 0, 'verified': 0, 'new': 0},
        'Tenders': {'total': 0, 'verified': 0, 'new': 0}
    }
    
    all_opportunities = []

    dirs = {
        'Equity': Path('01_equity'),
        'Grants': Path('02_grants'),
        'Tenders': Path('03_tenders')
    }
    
    week_ago = datetime.now() - timedelta(days=7)
    
    for cat, directory in dirs.items():
        if not directory.exists(): continue
        
        for f in directory.glob('*.md'):
            if f.name in ['template.md', 'registry_audit_log.md', 'global_audit_log.md']: continue
            
            stats[cat]['total'] += 1
            with open(f, 'r', encoding='utf-8') as content:
                text = content.read()

                # Basic parsing for JSON data
                title_match = re.search(r'^# (?:Tender Opportunity|Grant Opportunity|Equity Opportunity):?\s*(.*)', text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f.stem

                closing_match = re.search(r'-\s+\*\*Closing Date\*\*:\s*(.*)', text)
                closing = closing_match.group(1).strip() if closing_match else "N/A"

                inst_match = re.search(r'-\s+\*\*Institution\*\*:\s*(.*)', text)
                inst = inst_match.group(1).strip() if inst_match else "N/A"

                link_match = re.search(r'-\s+\*\*Direct Link\*\*:\s*(.*)', text)
                link = link_match.group(1).strip() if link_match else "#"

                is_verified = "VERIFIED" in text
                if is_verified:
                    stats[cat]['verified'] += 1

                is_new = datetime.fromtimestamp(f.stat().st_mtime) > week_ago
                if is_new:
                    stats[cat]['new'] += 1

                all_opportunities.append({
                    'id': f.stem,
                    'category': cat,
                    'title': title,
                    'institution': inst,
                    'closing_date': closing,
                    'link': link,
                    'path': str(f),
                    'verified': is_verified,
                    'new': is_new
                })

    # 2. Export JSON for GitHub Pages
    data_output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'stats': stats,
        'opportunities': all_opportunities,
        'published_files': [f.name for f in Path('published').glob('*') if f.is_file()]
    }
    
    with open(docs_dir / 'data.json', 'w', encoding='utf-8') as f:
        json.dump(data_output, f, indent=2)
    print(f"📄 Exported {len(all_opportunities)} opportunities to docs/data.json")

    # 3. Format Dashboard for README
    if readme_path.exists():
        total_opps = sum(s['total'] for s in stats.values())
        total_verified = sum(s['verified'] for s in stats.values())
        total_new = sum(s['new'] for s in stats.values())
        verify_pct = (total_verified / total_opps * 100) if total_opps > 0 else 0

        dashboard = f"""
## 🚀 Registry Status Dashboard
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

| Registry | Total | New (7d) | Verified | Health |
| :--- | :--- | :--- | :--- | :--- |
| 🏦 **Equity** | {stats['Equity']['total']} | {stats['Equity']['new']} | {stats['Equity']['verified']} | { '🟢' if stats['Equity']['total'] == stats['Equity']['verified'] else '🟡' } |
| 📜 **Grants** | {stats['Grants']['total']} | {stats['Grants']['new']} | {stats['Grants']['verified']} | { '🟢' if stats['Grants']['total'] == stats['Grants']['verified'] else '🟡' } |
| 🏗️ **Tenders** | {stats['Tenders']['total']} | {stats['Tenders']['new']} | {stats['Tenders']['verified']} | { '🟢' if stats['Tenders']['total'] == stats['Tenders']['verified'] else '🟡' } |

**Overall Progress**: `{verify_pct:.1f}%` Verified | `+{total_new}` New Opportunities This Week | [🌐 View Live Dashboard](https://rokctai.github.io/Opportunities-Registry/)
"""

        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        marker_start = "## 🚀 Registry Status Dashboard"
        if marker_start in readme_content:
            pattern = re.compile(rf"{marker_start}.*?(?=\n## )", re.DOTALL)
            if not pattern.search(readme_content):
                 pattern = re.compile(rf"{marker_start}.*", re.DOTALL)
            new_content = pattern.sub(dashboard.strip(), readme_content)
        else:
            parts = readme_content.split('\n\n', 1)
            if len(parts) > 1:
                new_content = parts[0] + "\n\n" + dashboard.strip() + "\n\n" + parts[1]
            else:
                new_content = readme_content + "\n\n" + dashboard.strip()

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ README Dashboard Updated.")

if __name__ == "__main__":
    update_readme_stats()
