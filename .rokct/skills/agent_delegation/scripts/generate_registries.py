# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import json
import re
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = Path('.')
REGISTRIES = {
    "Equity": BASE_DIR / "01_equity",
    "Grants": BASE_DIR / "02_grants",
    "Tenders": BASE_DIR / "03_tenders"
}
PUBLISHED_DIR = BASE_DIR / "published"
README_PATH = BASE_DIR / "README.md"
AUDIT_LOG_PATH = BASE_DIR / "03_tenders" / "registry_audit_log.md"

def scan_registry(name, path):
    """Scans a directory for markdown files and extracts stats."""
    total = 0
    verified = 0
    categories = {}
    
    if not path.exists():
        return 0, 0, {}

    for file in path.glob('*.md'):
        fname = file.name.lower()
        if fname in ['template.md', 'readme.md', 'registry_audit_log.md']:
            continue
        
        total += 1
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Logic: Tenders from API are "Verified" by default if Active
            if name == "Tenders" and "Status: ACTIVE" in content:
                verified += 1
            elif "Verification Status: VERIFIED" in content or "Status: VERIFIED" in content:
                verified += 1
            
            # Extract Category (Tenders specific)
            cat_match = re.search(r'### Category\n(.*?)\n', content, re.IGNORECASE)
            if cat_match:
                cat = cat_match.group(1).strip()
                categories[cat] = categories.get(cat, 0) + 1
            else:
                categories["Uncategorized"] = categories.get("Uncategorized", 0) + 1
                
    return total, verified, categories

def update_readme(stats):
    """Injects the latest stats into the README.md dashboard."""
    if not README_PATH.exists(): return
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prepare Dashboard Rows
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
    
    # 1. Replace Last Updated
    content = re.sub(
        r'\*Last Updated:.*?\*', 
        f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*", 
        content
    )
    
    # 2. Replace Table Content (more flexible regex)
    # This looks for the table header and replaces everything until the next double newline or progress marker
    table_pattern = r'(\| Registry \| Total \| New \(7d\) \| Verified \| Health \|\n\| :--- \| :--- \| :--- \| :--- \| :--- \|\n)([\s\S]*?)(?=\n\s*\n|\n\*\*Overall Progress\*\*)'
    content = re.sub(table_pattern, f'\\1{dashboard_table}', content)
    
    # 3. Replace Overall Progress
    progress_line = f"**Overall Progress**: `{verified_pct:.1f}%` Verified | `+{total_all}` New Opportunities This Week | [🌐 View Live Dashboard](https://rokctai.github.io/Opportunities-Registry/)"
    content = re.sub(r'\*\*Overall Progress\*\*:.*$', progress_line, content, flags=re.MULTILINE)

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ README.md Dashboard Updated.")

def update_audit_log(total, verified):
    """Updates the Tender-specific audit log."""
    if not AUDIT_LOG_PATH.exists(): return
    
    with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
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
            
    with open(AUDIT_LOG_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✅ registry_audit_log.md Updated.")

def generate():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Registry Orchestration...")
    
    stats = {}
    tender_categories = {}
    
    for name, path in REGISTRIES.items():
        total, verified, cats = scan_registry(name, path)
        stats[name] = (total, verified, cats)
        if name == "Tenders":
            tender_categories = cats

    # 1. Update README & Audit Log
    update_readme(stats)
    update_audit_log(stats["Tenders"][0], stats["Tenders"][1])

    # 2. Update meta.json
    meta_path = PUBLISHED_DIR / "api" / "meta.json"
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
        
    print(f"✅ meta.json updated with {stats['Tenders'][0]} tenders.")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Orchestration Complete.")

if __name__ == "__main__":
    generate()
