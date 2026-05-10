# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
import re
import time
import io
import pdfplumber

# --- CONFIGURATION ---
TENDER_DIR = Path('03_tenders')
SOURCES_DIR = TENDER_DIR / 'sources'

def get_musina_source_config():
    """Strictly reads URL and Flag from the musinaZA.md source card."""
    source_file = SOURCES_DIR / 'musinaZA.md'
    if not source_file.exists():
        raise FileNotFoundError(f"❌ Mandatory source card missing: {source_file}")
    
    config = {}
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
        u_match = re.search(r'-\s+\*\*URL\*\*:\s*(https?://[^\s\n]+)', content)
        if u_match: config["url"] = u_match.group(1).strip()
        else: raise ValueError(f"❌ URL missing in {source_file}")
        
        f_match = re.search(r'-\s+\*\*Flag\*\*:\s*([A-Z]{2})', content)
        if f_match: config["flag"] = f_match.group(1).strip()
        else: raise ValueError(f"❌ Flag missing in {source_file}")
            
    if not config["url"].endswith('/'): config["url"] += '/'
    config["source_card"] = f"sources/{source_file.name}"
    return config

SOURCE_CONFIG = get_musina_source_config()
BASE_URL = SOURCE_CONFIG["url"]
RFQ_URL = f"{BASE_URL}request-for-quotations/"
BIDS_URL = f"{BASE_URL}bids-received/"

def fetch_musina_rfqs():
    print(f"🚀 Scraping Musina RFQs from {RFQ_URL}...")
    try:
        response = requests.get(RFQ_URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        rfqs_found = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(" ", strip=True)
            url = link['href']

            rfq_match = re.search(r'RFQ\s*([\d/A-Z-]+)', text, re.IGNORECASE)
            if rfq_match:
                raw_id = rfq_match.group(1).strip().upper()
                full_id = f"RFQ{raw_id}" if not raw_id.startswith('RFQ') else raw_id

                title = text.replace(rfq_match.group(0), "").strip()
                if not title or len(title) < 5:
                    title = text

                parent = link.find_parent()
                pub_date = ""
                if parent:
                    parent_text = parent.get_text(" ", strip=True)
                    date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', parent_text)
                    if date_match:
                        pub_date = date_match.group(1)

                rfqs_found.append({
                    'id': full_id,
                    'title': title,
                    'url': url,
                    'pub_date': pub_date
                })

        best_rfqs = {}
        for r in rfqs_found:
            base_id_match = re.search(r'RFQ(\d+)', r['id'])
            base_id = base_id_match.group(0) if base_id_match else r['id']

            if base_id not in best_rfqs:
                best_rfqs[base_id] = r
            else:
                is_pdf = r['url'].lower().endswith('.pdf')
                prev_is_pdf = best_rfqs[base_id]['url'].lower().endswith('.pdf')
                if prev_is_pdf and not is_pdf:
                    best_rfqs[base_id] = r
                elif not prev_is_pdf and not is_pdf:
                    if len(r['title']) > len(best_rfqs[base_id]['title']):
                        best_rfqs[base_id] = r
                if len(r['id']) > len(best_rfqs[base_id]['id']):
                    best_rfqs[base_id]['id'] = r['id']

        count = 0
        for fid, rfq in best_rfqs.items():
            # fetch_deep_details always returns 3 values
            date_val, is_est, found_pub = fetch_deep_details(rfq['url'], rfq['pub_date'])

            if date_val:
                rfq['closing_date'] = f"{date_val}{' (Estimated)' if is_est else ''}"
            else:
                rfq['closing_date'] = "See Documents"

            if found_pub:
                rfq['pub_date'] = normalize_date(found_pub)
            elif rfq['pub_date']:
                rfq['pub_date'] = normalize_date(rfq['pub_date'])

            if sync_rfq_to_markdown(rfq):
                count += 1

        print(f"✅ Musina Sync complete. Processed {count} new/updated RFQs.")

    except Exception as e:
        print(f"❌ Error scraping Musina RFQs: {e}")

def fetch_deep_details(url, existing_pub):
    """Visits the detail page or parses PDF to extract dates."""
    if url.lower().endswith('.pdf'):
        pdf_date = extract_date_from_pdf(url)
        if pdf_date:
            return pdf_date, False, None
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

        # 1. Look for Publication Date
        found_pub = existing_pub
        pub_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})\s*[\s\|]+Musina Web', text_content)
        if pub_match:
            found_pub = pub_match.group(1).strip()

        # 2. Look for Closing Date
        patterns = [
            r'provided on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'on or before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'Closing date\s*[:\s]\s*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'Deadline\s*[:\s]\s*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'Closing Date\s*[:\s]\s*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                norm_date = normalize_date(date_str)
                if norm_date:
                    return norm_date, False, found_pub

        # 3. Try to find a PDF link on this page and parse it
        pdf_link = soup.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        if pdf_link:
            pdf_url = pdf_link['href']
            if not pdf_url.startswith('http'):
                pdf_url = "https://www.musina.gov.za" + pdf_url
            pdf_date = extract_date_from_pdf(pdf_url)
            if pdf_date:
                return pdf_date, False, found_pub

        val, est = calculate_fallback_date(found_pub)
        return val, est, found_pub
    except:
        val, est = calculate_fallback_date(existing_pub)
        return val, est, None

def extract_date_from_pdf(url):
    """Downloads and parses a PDF for a closing date."""
    try:
        print(f"📄 Attempting to parse PDF: {url}")
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200: return None

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
                    date_str = match.group(1).strip()
                    return normalize_date(date_str)
        return None
    except Exception as e:
        print(f"⚠️ PDF parsing failed for {url}: {e}")
        return None

def normalize_date(date_str):
    if not date_str: return None
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str): return date_str

    for fmt in ('%d %B %Y', '%d %b %Y', '%B %d, %Y', '%B %d %Y'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return date_str

def calculate_fallback_date(pub_date_str):
    if not pub_date_str:
        return None, False
    try:
        norm_pub = normalize_date(pub_date_str)
        if not norm_pub or not re.match(r'\d{4}-\d{2}-\d{2}', norm_pub):
            return None, False

        dt = datetime.strptime(norm_pub, '%Y-%m-%d')
        fallback = dt + timedelta(days=14)
        return fallback.strftime('%Y-%m-%d'), True
    except:
        return None, False

def is_expired(closing_date_str):
    if not closing_date_str or "See Documents" in closing_date_str:
        return False
    clean_date = closing_date_str.replace(" (Estimated)", "").strip()
    try:
        closing_date = datetime.strptime(clean_date, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return closing_date < today
    except:
        return False

def sync_rfq_to_markdown(rfq):
    base_id_match = re.search(r'RFQ(\d+)', rfq['id'])
    base_id = base_id_match.group(0).lower() if base_id_match else rfq['id'].lower().replace('/', '-').replace(' ', '-')
    filename = f"musina-{base_id}.md"
    file_path = TENDER_DIR / filename

    if is_expired(rfq['closing_date']):
        if file_path.exists():
            print(f"🔥 Deleting expired Musina RFQ: {filename} (Closed: {rfq['closing_date']})")
            os.remove(file_path)
        return False

    force_update = False
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # FLAG RECOVERY: If flag is missing but source card exists, inject it
            if f"- **Flag**: {REGION_FLAG}" not in content and "- **Flag**:" not in content:
                print(f"  🚩 Injecting missing flag ({REGION_FLAG}) into {filename}")
                new_line = f"- **Flag**: {REGION_FLAG}\n"
                # Inject after Source Card
                content = re.sub(r'(-\s+\*\*Source Card\*\*:[^\n]+\n)', r'\1' + new_line, content)
                with open(file_path, 'w', encoding='utf-8') as fw:
                    fw.write(content)

            if "Status: VERIFIED" in content or "Verification Status: VERIFIED" in content:
                return False

            m = re.search(r'-\s+\*\*Closing Date\*\*:\s*(.+)$', content, re.MULTILINE)
            current_date = m.group(1).strip() if m else ""
            if current_date != rfq['closing_date']:
                force_update = True

            m_pub = re.search(r'-\s+\*\*Date Published\*\*:\s*(.*)$', content, re.MULTILINE)
            current_pub = m_pub.group(1).strip() if m_pub else ""
            if current_pub != rfq['pub_date']:
                force_update = True

    if not file_path.exists() or force_update:
        md = f"""# Tender Opportunity: {rfq['title']}

## Quick Stats
- **Tender Number**: {rfq['id']}
- **Institution**: Musina Local Municipality
- **Source Card**: {SOURCE_CARD_REF}
- **Flag**: {REGION_FLAG}
- **Tender Type**: Request for Quotation
- **Province**: Limpopo
- **Date Published**: {rfq['pub_date'] or ''}
- **Closing Date**: {rfq['closing_date']}
- **Place Required**: Musina

## Detailed Description
### Category
General Procurement

### Tender Description
{rfq['title']}

### Special Conditions
See attached RFQ document for compliance requirements and submission details.

## Briefing Session
- **Is there a briefing session?**: No (Check Documents)
- **Is it compulsory?**: No
- **Briefing Date and Time**: N/A
- **Briefing Venue**: N/A

## Enquiries
- **Contact Person**: SCM Department
- **Email**: rfq@musina.gov.za
- **Telephone**: 015 534 6100

## Documents & Links
- **Direct Link**: {rfq['url']}
- **Tender Documents**:
    - [Download RFQ Document]({rfq['url']})

## Audit & Status
- **Status**: ACTIVE
- **Last Verified**: {datetime.now().strftime('%Y-%m-%d')}

## AI Checklist (Jules)
- [ ] Review RFQ requirements and mandatory documents | 1
- [ ] Verify closing date and submission email | 1
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md)
        return True
    return False

def fetch_musina_bids():
    print(f"🚀 Scraping Musina Bids Received from {BIDS_URL}...")
    try:
        response = requests.get(BIDS_URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        bids = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(" ", strip=True)
            if "TENDER NO" in text.upper() or "BID RECEIVED" in text.upper():
                bids.append(text)

        if bids:
            log_path = Path('.rokct/agent/logs/musina_bids_intelligence.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n--- Audit: {datetime.now().isoformat()} ---\n")
                for bid in bids:
                    f.write(f"{bid}\n")
            print(f"📊 Logged {len(bids)} bid entries for competitive intelligence.")

    except Exception as e:
        print(f"❌ Error scraping Musina Bids: {e}")

if __name__ == "__main__":
    TENDER_DIR.mkdir(parents=True, exist_ok=True)
    fetch_musina_rfqs()
    fetch_musina_bids()
