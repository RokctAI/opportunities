# Licensed under the MIT License.
# Copyright 2024 RokctAI

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def run_sync(tender_dir, sources_dir, generate_md_fn):
    """Resilient Musina Scraper with Automated Flag Recovery."""
    print("[Musina] Starting Scraper Sync...")
    
    # 1. Load Config
    source_file = sources_dir / 'musinaZA.md'
    if not source_file.exists():
        print("  [Error] Musina source card missing.")
        return
        
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
        u_match = re.search(r'URL\*\*:\s*(https?://[^\s\n]+)', content)
        f_match = re.search(r'Flag\*\*:\s*([A-Z]{2})', content)
        if not u_match or not f_match:
            print("  [Error] Musina config incomplete.")
            return
        base_url = u_match.group(1).strip()
        if not base_url.endswith('/'): base_url += '/'
        flag = f_match.group(1).strip()
        source_ref = f"sources/{source_file.name}"

    # 2. Resilient Session
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2)))
    session.headers.update({'User-Agent': 'Mozilla/5.0 RokctAI-Scraper/1.0'})

    try:
        rfq_url = f"{base_url}request-for-quotations/"
        response = session.get(rfq_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        updates = 0
        for link in soup.find_all('a', href=True):
            text = link.get_text(" ", strip=True)
            url = link['href']
            if not url.startswith('http'): url = "https://www.musina.gov.za" + url

            rfq_match = re.search(r'RFQ\s*([\d/A-Z-]+)', text, re.I)
            if rfq_match:
                raw_id = rfq_match.group(1).strip().upper()
                full_id = f"musina-rfq{raw_id.lower().replace('/', '-')}"
                
                # Create a mock OCDS-style release for the universal generator
                release = {
                    "ocid": full_id,
                    "date": datetime.now().isoformat(),
                    "tender": {
                        "title": text,
                        "procuringEntity": {"name": "Musina Local Municipality"},
                        "procurementMethodDetails": "Request for Quotation",
                        "province": "Limpopo",
                        "deliveryLocation": "Musina",
                        "category": "General Procurement",
                        "description": text,
                        "documents": [{"title": "RFQ Document", "url": url}]
                    }
                }

                fpath = tender_dir / f"{full_id}.md"
                existing = ""
                if fpath.exists():
                    with open(fpath, 'r', encoding='utf-8') as f:
                        existing = f.read()
                    if "VERIFIED" in existing: continue

                new_c = generate_md_fn(release, flag, source_ref)
                
                if [l.strip() for l in existing.splitlines() if l.strip()] != [l.strip() for l in new_c.splitlines() if l.strip()]:
                    with open(fpath, 'w', encoding='utf-8', newline='\n') as fw:
                        fw.write(new_c)
                    updates += 1
                    
        print(f"  [+] Musina: Updated {updates} items.")
    except Exception as e:
        print(f"  [Error] Musina sync failed: {e}")
