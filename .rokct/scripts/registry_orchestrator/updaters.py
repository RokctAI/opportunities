# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
import json
from datetime import datetime
from pathlib import Path

def update_readme(readme_path, stats):
    """Injects the latest stats into the README.md dashboard."""
    if not readme_path.exists(): return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    rows = []
    total_all = 0
    verified_all = 0
    icons = {"Equity": "🏦", "Grants": "📜", "Tenders": "🏗️"}
    
    for name, data in stats.items():
        total, verified, _ = data
        health = "🟢" if verified > (total * 0.8) else "🟡"
        rows.append(f"| {icons.get(name, '📁')} **{name}** | {total} | {total} | {verified} | {health} |")
        total_all += total
        verified_all += verified

    dashboard_table = "\n".join(rows)
    verified_pct = (verified_all / total_all * 100) if total_all > 0 else 0
    
    content = re.sub(r'\*Last Updated:.*?\*', f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*", content)
    table_pattern = r'(\| Registry \| Total \| New \(7d\) \| Verified \| Health \|\n\| :--- \| :--- \| :--- \| :--- \| :--- \|\n)([\s\S]*?)(?=\n\s*\n|\n\*\*Overall Progress\*\*)'
    content = re.sub(table_pattern, f'\\1{dashboard_table}', content)
    progress_line = f"**Overall Progress**: `{verified_pct:.1f}%` Verified | `+{total_all}` New Opportunities This Week | [🌐 View Live Dashboard](https://rokctai.github.io/Opportunities-Registry/)"
    content = re.sub(r'\*\*Overall Progress\*\*:.*$', progress_line, content, flags=re.MULTILINE)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_audit_log(audit_path, total, verified):
    """Updates the Tender-specific audit log."""
    if not audit_path.exists(): return
    
    with open(audit_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith("| 03_tenders/ |"):
            new_lines.append(f"| 03_tenders/ | LIVING | IN_PROGRESS | {datetime.now().strftime('%Y-%m-%d')} | {verified} | {total} |\n")
        elif "Automated audit log update:" in line:
            new_lines.append(f"- Automated audit log update: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        elif "Verified:" in line:
            pct = (verified / total * 100) if total > 0 else 0
            new_lines.append(f"- Verified: {verified}/{total} ({pct:.1f}%)\n")
        else:
            new_lines.append(line)
            
    with open(audit_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def update_json_meta(meta_path, stats, tender_categories):
    """Generates the meta.json file."""
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_data = {
        "last_sync": datetime.now().isoformat(),
        "total_tenders": stats["Tenders"][0],
        "verified_tenders": stats["Tenders"][1],
        "categories": tender_categories,
        "registries": {k: {"total": v[0], "verified": v[1]} for k, v in stats.items()}
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, indent=2)
