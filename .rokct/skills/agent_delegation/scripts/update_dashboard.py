# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
from pathlib import Path
from datetime import datetime, timedelta

def update_readme_stats():
    """Calculates registry stats and updates the main README.md."""
    print("📊 Updating README Statistics Dashboard...")
    
    project_root = Path(__file__).parent.parent.parent.parent.parent
    readme_path = project_root / 'README.md'
    
    if not readme_path.exists():
        print("❌ README.md not found.")
        return

    # 1. Calculate Stats
    stats = {
        'Equity': {'total': 0, 'verified': 0, 'new': 0},
        'Grants': {'total': 0, 'verified': 0, 'new': 0},
        'Tenders': {'total': 0, 'verified': 0, 'new': 0}
    }
    
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
                if "VERIFIED" in text:
                    stats[cat]['verified'] += 1
            
            if datetime.fromtimestamp(f.stat().st_mtime) > week_ago:
                stats[cat]['new'] += 1

    # 2. Format Dashboard
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

**Overall Progress**: `{verify_pct:.1f}%` Verified | `+{total_new}` New Opportunities This Week
"""

    # 3. Inject into README
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Look for the section or append
    marker_start = "## 🚀 Registry Status Dashboard"
    if marker_start in readme_content:
        # Replace existing
        # Find start of next ## section or end of file
        pattern = re.compile(rf"{marker_start}.*?(?=\n## )", re.DOTALL)
        if not pattern.search(readme_content): # Handle if it is the last section
             pattern = re.compile(rf"{marker_start}.*", re.DOTALL)
        new_content = pattern.sub(dashboard.strip(), readme_content)
    else:
        # Append to top after first heading
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
