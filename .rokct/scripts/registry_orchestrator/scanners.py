# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path
from healers import heal_equity_flags

# --- THE GOLDEN DEFAULTS ---
DEFAULT_AI_BLOCK = """- [ ] Review Tender Documents | 1
- [ ] Prepare Initial Response | 3"""

def scan_registry(name, path):
    """Scans a directory with deep metadata extraction and auto-healing."""
    total = 0
    verified = 0
    stats_aggregation = {} 
    advanced_tenders = {}
    todo_list = []
    
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
                
                # --- HEALING STEP ---
                if name == "Equity":
                    # Automatically add missing flags based on Country
                    content = heal_equity_flags(file, content)

                # --- SCANNING LOGIC ---
                # 1. Verification Logic
                is_active = re.search(r'-\s+\*\*Status\*\*:\s*ACTIVE', content, re.I)
                is_verified = re.search(r'Verification Status:\s*VERIFIED', content, re.I)
                
                if is_active or is_verified:
                    verified += 1
                
                # 2. Universal Metadata Extraction
                stat_matches = re.finditer(r'-\s+\*\*(?P<key>.*?)\*\*:\s*(?P<val>.*)', content)
                for m in stat_matches:
                    key = m.group('key').strip()
                    val = m.group('val').strip()
                    if key not in stats_aggregation: stats_aggregation[key] = {}
                    stats_aggregation[key][val] = stats_aggregation[key].get(val, 0) + 1

                # 3. Tender AI Logic
                if name == "Tenders":
                    match = re.search(r'## AI Checklist \(Jules\)[\s\S]*?-->\s*([\s\S]*)$', content)
                    if match:
                        current_tasks = match.group(1).strip()
                        if current_tasks != DEFAULT_AI_BLOCK and len(current_tasks) > 10:
                            advanced_tenders[file.stem] = {
                                "enrichment": "ADVANCED",
                                "tasks": [t.strip('- [ ]').strip() for t in current_tasks.splitlines() if t.strip()]
                            }
                        else:
                            todo_list.append(str(file.relative_to(path.parent.parent)))
                            
        except Exception:
            continue
                
    return total, verified, stats_aggregation, advanced_tenders, todo_list
