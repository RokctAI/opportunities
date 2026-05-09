# Licensed under the MIT License.
# Copyright 2026 RokctAI

import os
import json
import re
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
DATA_MAP = {
    '01_equity': 'equity.json',
    '02_grants': 'grants.json',
    '03_tenders': 'tenders.json'
}
CLASSIFICATION_PATH = Path('.rokct/config/classifications')

def load_classifications():
    """Loads standardized classifications if they exist."""
    classes = {}
    if CLASSIFICATION_PATH.exists():
        # Implementation could be extended to read specific mapping files
        pass
    return classes

def parse_markdown_card(content):
    """Parses a markdown card into a dictionary with improved metadata extraction."""
    data = {}
    
    # Extract Title (h1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    data['title'] = title_match.group(1).strip() if title_match else "Unknown"
    
    # Extract Key-Value pairs from bullets
    # Matches: - **Key**: Value
    matches = re.findall(r'-\s+\*\*(.+?)\*\*:\s*(.*)', content)
    for key, val in matches:
        clean_key = key.lower().replace(' ', '_').strip('?')
        data[clean_key] = val.strip()
    
    # Ensure mandatory metadata fields exist (even if empty)
    for field in ['flag', 'source_card', 'status', 'last_verified']:
        if field not in data:
            data[field] = "N/A"
            
    # Category Extraction
    category = "General"
    cat_match = re.search(r'### Category\n\s*(.+)', content)
    if cat_match:
        category = cat_match.group(1).strip()
    data['category'] = category
        
    return data

def generate_registries():
    print("🚀 Generating Enhanced JSON Database...")
    
    meta = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "registries": {}
    }
    
    api_dir = Path('published/api')
    api_dir.mkdir(parents=True, exist_ok=True)
    
    for folder, output_file in DATA_MAP.items():
        folder_path = Path(folder)
        if not folder_path.exists(): continue
            
        items = []
        category_counts = {}
        last_item_update = None
        
        reg_name = folder.split('_')[1]
        print(f"📦 Indexing {reg_name}...")
        
        for md_file in folder_path.glob('*.md'):
            if md_file.name in ['template.md', 'registry_audit_log.md', 'global_audit_log.md']:
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    item_data = parse_markdown_card(content)
                    item_data['slug'] = md_file.stem
                    items.append(item_data)
                    
                    # Track breakdown by category
                    cat = item_data.get('category', 'General')
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    
                    # Track latest update
                    updated_at = item_data.get('last_verified')
                    if updated_at and updated_at != "N/A":
                        if not last_item_update or updated_at > last_item_update:
                            last_item_update = updated_at
                            
            except Exception as e:
                print(f"❌ Error parsing {md_file}: {e}")
        
        # Save Registry JSON
        with open(api_dir / output_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
            
        # Update Meta with detailed breakdown
        meta['registries'][reg_name] = {
            "total_count": len(items),
            "breakdown": category_counts,
            "last_verified": last_item_update if last_item_update else "N/A",
            "endpoint": f"/api/{output_file}"
        }
        
    # Save Meta JSON
    with open(api_dir / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
        
    print(f"✅ JSON Database regenerated at {api_dir}/")

if __name__ == "__main__":
    generate_registries()
