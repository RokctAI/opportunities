# Licensed under the MIT License.
# Copyright 2024 RokctAI

import requests
import re
from datetime import datetime, timedelta
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def run_sync(tender_dir, sources_dir, generate_md_fn):
    """Resilient OCDS Sync with Latest-First Deduplication."""
    print("[OCDS] Starting API Sync (Window: 7 days, PageSize: 5000)...")
    
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))
    session.headers.update({'User-Agent': 'Mozilla/5.0 RokctAI-Resilient-Sync/1.0'})

    # 1. Discover OCDS Sources
    configs = []
    if sources_dir.exists():
        for sf in sources_dir.glob('*.md'):
            with open(sf, 'r', encoding='utf-8') as f:
                content = f.read()
                # Robust Regex check
                if re.search(r'-\s+\*\*Is API\*\*:\s*true', content, re.I) and 'OCDS' in content:
                    u_match = re.search(r'URL\*\*:\s*(https?://[^\s\n]+)', content)
                    f_match = re.search(r'Flag\*\*:\s*([A-Z]{2})', content)
                    if u_match and f_match:
                        configs.append({
                            "url": u_match.group(1).strip(), 
                            "flag": f_match.group(1).strip(), 
                            "ref": f"sources/{sf.name}"
                        })
    
    # 2. Sync each source
    for c in configs:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        params = {"PageNumber": 1, "PageSize": 5000, "dateFrom": date_from}
        
        try:
            resp = session.get(c['url'], params=params, timeout=120)
            resp.raise_for_status()
            releases = resp.json().get('releases', [])
            
            # --- DEDUPLICATION: Latest first ---
            latest_map = {}
            for r in releases:
                ocid = r.get('ocid')
                if ocid and (ocid not in latest_map or r.get('date', '') > latest_map[ocid].get('date', '')):
                    latest_map[ocid] = r
            
            updates = 0
            for ocid, rel in latest_map.items():
                fpath = tender_dir / f"{ocid}.md"
                
                # Load existing for robust comparison
                existing = ""
                if fpath.exists():
                    with open(fpath, 'r', encoding='utf-8') as f:
                        existing = f.read()
                    if "Verification Status: VERIFIED" in existing:
                        continue
                
                new_c = generate_md_fn(rel, c['flag'], c['ref'])
                
                # Robust line-by-line comparison
                if [l.strip() for l in existing.splitlines() if l.strip()] != [l.strip() for l in new_c.splitlines() if l.strip()]:
                    with open(fpath, 'w', encoding='utf-8', newline='\n') as fw:
                        fw.write(new_c)
                    updates += 1
            
            print(f"  [+] {c['flag']}: Received {len(releases)} releases. Updated {updates} files.")
        except Exception as e:
            print(f"  [Error] Failed to sync {c['flag']}: {e}")
