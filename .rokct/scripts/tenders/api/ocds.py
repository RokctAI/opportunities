# Licensed under the MIT License.
import requests, re, os
from datetime import datetime, timedelta
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def run_sync(tender_dir, sources_dir, generate_md_fn):
    print("[OCDS] Starting API Sync...")
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2)))
    
    # Discovery
    configs = []
    for sf in sources_dir.glob('*.md'):
        with open(sf, 'r', encoding='utf-8') as f:
            content = f.read()
            if '**Is API**: true' in content and 'OCDS' in content:
                u = re.search(r'URL\*\*:\s*(https?://[^\s\n]+)', content)
                f_match = re.search(r'Flag\*\*:\s*([A-Z]{2})', content)
                if u and f_match:
                    configs.append({"url": u.group(1).strip(), "flag": f_match.group(1).strip(), "ref": f"sources/{sf.name}"})
    
    for c in configs:
        params = {"PageNumber": 1, "PageSize": 5000, "dateFrom": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}
        try:
            resp = session.get(c['url'], params=params, timeout=120)
            releases = resp.json().get('releases', [])
            updates = 0
            for r in releases:
                ocid = r.get('ocid')
                fpath = tender_dir / f"{ocid}.md"
                if fpath.exists() and "VERIFIED" in open(fpath, 'r', encoding='utf-8').read(): continue
                new_c = generate_md_fn(r, c['flag'], c['ref'])
                with open(fpath, 'w', encoding='utf-8', newline='\n') as fw: fw.write(new_c)
                updates += 1
            print(f"  [+] {c['flag']}: {updates} updates.")
        except Exception as e: print(f"  [Error] {e}")
