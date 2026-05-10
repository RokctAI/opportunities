# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path

# --- THE GOLDEN DEFAULTS ---
# This is what CI uses to detect if Jules has done her work.
DEFAULT_AI_BLOCK = """- [ ] Review Tender Documents | 1
- [ ] Prepare Initial Response | 3"""

def scan_registry(name, path):
    """Scans a directory and detects if AI enrichment has happened."""
    total = 0
    verified = 0
    categories = {}
    advanced_tenders = {} # OCID -> Custom Tasks
    todo_list = [] # List of paths for Jules to work on
    
    if not path.exists():
        return 0, 0, {}, {}, []

    for file in path.glob('*.md'):
        fname = file.name.lower()
        if fname in ['template.md', 'readme.md', 'registry_audit_log.md'] or fname.startswith('registry_'):
            continue
        
        total += 1
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if name == "Tenders":
                    # 1. Verification Logic
                    if "Status: ACTIVE" in content or "VERIFIED" in content:
                        verified += 1
                    
                    # 2. AI Enrichment Detection
                    # We look for the section below the Jules header
                    match = re.search(r'## AI Checklist \(Jules\)[\s\S]*?-->\s*([\s\S]*)$', content)
                    if match:
                        current_tasks = match.group(1).strip()
                        # Compare against defaults
                        if current_tasks != DEFAULT_AI_BLOCK and len(current_tasks) > 10:
                            # Jules has worked on this!
                            advanced_tenders[file.stem] = {
                                "enrichment": "ADVANCED",
                                "tasks": [t.strip('- [ ]').strip() for t in current_tasks.splitlines() if t.strip()]
                            }
                        else:
                            # Still basic - add to Jules' Todo List
                            todo_list.append(str(file.relative_to(path.parent.parent)))
                
                elif "VERIFIED" in content:
                    verified += 1
                
                # Category Extraction
                cat_match = re.search(r'### Category\n(.*?)\n', content, re.IGNORECASE)
                if cat_match:
                    cat = cat_match.group(1).strip()
                    categories[cat] = categories.get(cat, 0) + 1
        except Exception:
            continue
                
    return total, verified, categories, advanced_tenders, todo_list
