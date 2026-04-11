# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
from pathlib import Path

def generate_response_kits():
    """Generates a starting bid package for verified tenders."""
    print("📂 Checking for Tenders ready for Response Kits...")
    
    tenders_dir = Path('03_tenders')
    responses_dir = Path('responses')
    
    if not tenders_dir.exists(): return

    for md_file in tenders_dir.glob('ocid-*.md'):
        with open(md_file, 'r') as f:
            content = f.read()
            
        # Only create kits for VERIFIED opportunities
        if "Verification Status: VERIFIED" in content or "Status: VERIFIED" in content:
            # Extract metadata
            title_match = re.search(r'# Tender Opportunity:\s*(.+)', content)
            id_match = re.search(r'-\s+\*\*Tender Number\*\*:\s*(.+)', content)
            
            if not title_match or not id_match: continue
            
            tender_id = id_match.group(1).strip()
            tender_title = title_match.group(1).strip()
            safe_name = "".join([c if c.isalnum() else "_" for c in tender_title])[:50]
            
            kit_dir = responses_dir / f"{tender_id}_{safe_name}"
            if not kit_dir.exists():
                kit_dir.mkdir(parents=True, exist_ok=True)
                
                # Create Template Response
                with open(kit_dir / 'proposal_draft.md', 'w') as p:
                    p.write(f"# Proposal for {tender_title}\n\n"
                            f"## Opportunity Details\n"
                            f"- **ID**: {tender_id}\n"
                            f"- **Status**: Verified\n\n"
                            f"## Compliance Checklist\n"
                            f"- [ ] B-BBEE Certificate\n"
                            f"- [ ] Tax Clearance\n"
                            f"- [ ] CSD Registration\n\n"
                            f"## Response Sections\n"
                            f"### 1. Executive Summary\n\n"
                            f"### 2. Methodology\n\n"
                            f"### 3. Pricing Schedule\n")
                
                print(f"✅ Created Response Kit: {kit_dir.name}")

if __name__ == "__main__":
    generate_response_kits()
