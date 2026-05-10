# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path

def scan_registry(name, path):
    """Scans a directory for markdown files and extracts stats."""
    total = 0
    verified = 0
    categories = {}
    
    if not path.exists():
        return 0, 0, {}

    for file in path.glob('*.md'):
        fname = file.name.lower()
        # Exclude management files and templates
        if fname in ['template.md', 'readme.md', 'registry_audit_log.md'] or fname.startswith('registry_'):
            continue
        
        total += 1
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Logic: Tenders from API are "Verified" by default if Active
                if name == "Tenders" and "Status: ACTIVE" in content:
                    verified += 1
                elif "Verification Status: VERIFIED" in content or "Status: VERIFIED" in content:
                    verified += 1
                
                # Extract Category
                cat_match = re.search(r'### Category\n(.*?)\n', content, re.IGNORECASE)
                if cat_match:
                    cat = cat_match.group(1).strip()
                    categories[cat] = categories.get(cat, 0) + 1
                else:
                    categories["Uncategorized"] = categories.get("Uncategorized", 0) + 1
        except Exception:
            continue
                
    return total, verified, categories
