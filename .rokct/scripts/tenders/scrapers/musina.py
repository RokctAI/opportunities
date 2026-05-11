# Licensed under the MIT License.
# Copyright 2024 RokctAI

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
import re
import io
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def normalize_date(date_str):
    if not date_str:
        return None
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    for fmt in ('%d %B %Y', '%d %b %Y', '%B %d, %Y', '%B %d %Y'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return date_str


def calculate_fallback_date(pub_date_str):
    """Returns (date_str, is_estimated). Adds 14 days to pub date as a fallback."""
    if not pub_date_str:
        return None, False
    try:
        norm = normalize_date(pub_date_str)
        if not norm or not re.match(r'\d{4}-\d{2}-\d{2}', norm):
            return None, False
        dt = datetime.strptime(norm, '%Y-%m-%d')
        return (dt + timedelta(days=14)).strftime('%Y-%m-%d'), True
    except:
        return None, False


def extract_date_from_pdf(url):
    if not pdfplumber:
        return None
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            return None
        with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
            text = ""
            for i in range(min(len(pdf.pages), 2)):
                text += pdf.pages[i].extract_text() or ""
            patterns = [
                r'provided on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
                r'on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
                r'Closing date\s*[:\s]\s*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
                r'Closing Date\s*[:\s]\s*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return normalize_date(match.group(1).strip())
    except:
        pass
    return None


def fetch_deep_details(url, existing_pub):
    """Visits the detail page or parses PDF to extract dates.
    Returns (closing_date, is_estimated, found_pub_date).
    When no closing date is found, falls back to pub_date + 14 days (is_estimated=True).
    When pub_date is also unknown, returns (None, False, ...) → caller sets 'See Documents'.
    """
    if url.lower().endswith('.pdf'):
        pdf_date = extract_date_from_pdf(url)
        if pdf_date:
            return pdf_date, False, None
        # Fallback: estimate from existing pub date
        val, est = calculate_fallback_date(existing_pub)
        return val, est, None

    try:
        time.sleep(0.5)
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            val, est = calculate_fallback_date(existing_pub)
            return val, est, None

        soup = BeautifulSoup(resp.text, 'lxml')
        text_content = soup.get_text(" ", strip=True)

        # 1. Look for Publication Date on the page
        found_pub = existing_pub
        pub_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})\s*[\s\|]+Musina Web', text_content)
        if pub_match:
            found_pub = pub_match.group(1).strip()

        # 2. Look for Closing Date patterns
        patterns = [
            r'provided on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                norm = normalize_date(match.group(1).strip())
                if norm:
                    return norm, False, found_pub

        # 3. Try to find and parse a linked PDF
        pdf_link = soup.find('a', href=re.compile(r'\.pdf$', re.I))
        if pdf_link:
            pdf_url = pdf_link['href']
            if not pdf_url.startswith('http'):
                pdf_url = "https://www.musina.gov.za" + pdf_url
            pdf_date = extract_date_from_pdf(pdf_url)
            if pdf_date:
                return pdf_date, False, found_pub

        # 4. Nothing found — fall back to pub date + 14 days
        val, est = calculate_fallback_date(found_pub)
        return val, est, found_pub

    except:
        val, est = calculate_fallback_date(existing_pub)
        return val, est, None


def run_sync(tender_dir, sources_dir, generate_md_fn):
    print("[Musina] Starting Scraper Sync...")
    source_file = sources_dir / 'musinaZA.md'
    if not source_file.exists():
        return

    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
        u_match = re.search(r'URL\*\*:\s*(https?://[^\s\n]+)', content)
        f_match = re.search(r'Flag\*\*:\s*([A-Z]{2})', content)
        if not u_match or not f_match:
            return
        base_url = u_match.group(1).strip()
        if not base_url.endswith('/'):
            base_url += '/'
        flag = f_match.group(1).strip()
        source_ref = f"sources/{source_file.name}"

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2)))
    session.headers.update({'User-Agent': 'Mozilla/5.0 RokctAI-Scraper/1.0'})

    # 1. Bids Received Intelligence
    log_path = Path(__file__).parent.parent.parent.parent / '.rokct' / 'agent' / 'logs' / 'musina_bids_intelligence.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    audit_entries = []

    try:
        b_resp = session.get(f"{base_url}bids-received/", timeout=30)
        if b_resp.status_code == 200:
            b_soup = BeautifulSoup(b_resp.text, 'lxml')
            for b_link in b_soup.find_all('a', href=True):
                b_text = b_link.get_text(" ", strip=True)
                if any(kw in b_text.upper() for kw in ["TENDER", "RFQ", "BID"]):
                    audit_entries.append(f"BID RECEIVED - {b_text}")
    except:
        pass

    # 2. RFQ Scraping
    try:
        response = session.get(f"{base_url}request-for-quotations/", timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        rfqs_found = {}
        for link in soup.find_all('a', href=True):
            text = link.get_text(" ", strip=True)
            url = link['href']
            if not url.startswith('http'):
                url = "https://www.musina.gov.za" + url

            if any(kw in text.upper() for kw in ["TENDER", "RFQ", "BID"]):
                audit_entries.append(text)

            rfq_match = re.search(r'RFQ\s*([\d/A-Z-]+)', text, re.I)
            if rfq_match:
                raw_full = rfq_match.group(1).strip().upper()
                # DEDUPLICATION: Extract just the numeric ID (e.g., 59 from 59/2024)
                base_id_match = re.search(r'(\d+)', raw_full)
                base_id = base_id_match.group(1) if base_id_match else raw_full.replace('/', '-')
                full_id = f"musina-rfq{base_id}"

                pub_date = ""
                parent = link.find_parent()
                if parent:
                    date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', parent.get_text())
                    if date_match:
                        pub_date = date_match.group(1)

                if full_id not in rfqs_found:
                    rfqs_found[full_id] = {'text': text, 'url': url, 'pub': pub_date}
                else:
                    # Prefer PDF links if duplicates exist
                    if url.lower().endswith('.pdf'):
                        rfqs_found[full_id] = {'text': text, 'url': url, 'pub': pub_date}

        updates = 0
        for fid, rdata in rfqs_found.items():
            fpath = tender_dir / f"{fid}.md"
            existing = ""
            if fpath.exists():
                with open(fpath, 'r', encoding='utf-8') as f:
                    existing = f.read()
                if "VERIFIED" in existing:
                    continue

            closing_date, is_est, found_pub = fetch_deep_details(rdata['url'], rdata['pub'])

            final_pub = normalize_date(found_pub) or normalize_date(rdata['pub']) or ""

            # Apply (Estimated) suffix when date is a fallback, "See Documents" when unknown
            if closing_date:
                final_close = f"{closing_date} (Estimated)" if is_est else closing_date
            else:
                final_close = "See Documents"

            release = {
                "ocid": fid,
                "date": final_pub,
                "tender": {
                    "title": rdata['text'],
                    "procuringEntity": {"name": "Musina Local Municipality"},
                    "procurementMethodDetails": "Request for Quotation",
                    "province": "Limpopo",
                    "deliveryLocation": "Musina",
                    "category": "General Procurement",
                    "description": rdata['text'],
                    "tenderPeriod": {"endDate": final_close},
                    "documents": [{"title": "RFQ Document", "url": rdata['url']}]
                }
            }

            new_c = generate_md_fn(release, flag, source_ref, existing)
            if [l.strip() for l in existing.splitlines() if l.strip()] != [l.strip() for l in new_c.splitlines() if l.strip()]:
                with open(fpath, 'w', encoding='utf-8', newline='\n') as fw:
                    fw.write(new_c)
                updates += 1

        if audit_entries:
            with open(log_path, 'a', encoding='utf-8') as log_f:
                log_f.write(f"\n--- Audit: {datetime.now().isoformat()} ---\n")
                for entry in audit_entries:
                    log_f.write(f"{entry}\n")

        print(f"  [+] Musina: Updated {updates} items. Intelligence log updated.")

    except Exception as e:
        print(f"  [Error] Musina sync failed: {e}")
        if "Timeout" in str(e) or "Max retries exceeded" in str(e):
            print("🚨 Musina site is likely broken or down. Skipping.")