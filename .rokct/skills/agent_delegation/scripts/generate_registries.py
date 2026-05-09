# Licensed under the MIT License.
# Copyright 2026 RokctAI

import os
import json
import re
from pathlib import Path
from datetime import datetime

def parse_markdown_card(content):
    """Parses a markdown card into a dictionary using regex for speed."""
    data = {}
    
    # Extract Title (h1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    data['title'] = title_match.group(1).strip() if title_match else "Unknown"
    
    # Extract Key-Value pairs from bullets
    # Matches: - **Key**: Value
    matches = re.findall(r'-\s+\*\*(.+?)\*\*:\s*(.*)', content)
    for key, val in matches:
        data[key.lower().replace(' ', '_')] = val.strip()
    
    # Special section extraction: AI Analysis / Description
    # Matches from ## Detailed Description until next ##
    desc_match = re.search(r'## Detailed Description\s*\n\s*([\s\S]+?)\n\n##', content)
    if desc_match:
        data['description'] = desc_match.group(1).strip()
        
    return data

def generate_registries():
    print("🚀 Generating optimized JSON registries...")
    
    data_map = {
        '01_equity': 'equity.json',
        '02_grants': 'grants.json',
        '03_tenders': 'tenders.json'
    }
    
    meta = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "categories": {}
    }
    
    api_dir = Path('published/api')
    api_dir.mkdir(parents=True, exist_ok=True)
    
    for folder, output_file in data_map.items():
        folder_path = Path(folder)
        if not folder_path.exists():
            print(f"⚠️ Folder {folder} not found. Skipping.")
            continue
            
        items = []
        last_item_update = None
        
        print(f"📦 Processing {folder}...")
        for md_file in folder_path.glob('*.md'):
            # Skip templates and logs
            if md_file.name in ['template.md', 'registry_audit_log.md', 'global_audit_log.md']:
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    item_data = parse_markdown_card(content)
                    item_data['slug'] = md_file.stem
                    items.append(item_data)
                    
                    # Track latest update in this category
                    updated_at = item_data.get('last_verified')
                    if updated_at:
                        if not last_item_update or updated_at > last_item_update:
                            last_item_update = updated_at
            except Exception as e:
                print(f"❌ Error parsing {md_file}: {e}")
        
        # Save Category JSON
        with open(api_dir / output_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
            
        # Update Meta
        meta['categories'][folder.split('_')[1]] = {
            "count": len(items),
            "last_updated": last_item_update + "T00:00:00Z" if last_item_update else meta['last_updated'],
            "endpoint": f"/api/{output_file}"
        }
        
    # Save Meta JSON
    with open(api_dir / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
        
    print(f"✅ Registries generated in {api_dir}/")

if __name__ == "__main__":
    generate_registries()
