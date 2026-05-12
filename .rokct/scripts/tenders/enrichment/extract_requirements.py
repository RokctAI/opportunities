import pdfplumber
import re
import sys
import json
import requests
import io
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def extract_requirements_from_pdf(pdf_stream):
    """Extracts Mandatory Documents (Gate 1) and Functional Criteria (Gate 2) from a PDF stream."""
    results = {
        "gate_1_mandatory": [],
        "gate_2_functional": [],
        "pricing_preference": "Unknown"
    }

    try:
        with pdfplumber.open(pdf_stream) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])

            # 1. Gate 1 (Mandatory)
            gate_1_patterns = [
                r'SBD\s*\d', r'MBD\s*\d', r'CSD\s*report', r'Tax\s*compliance',
                r'B-BBEE\s*(?:certificate|affidavit)', r'COIDA', r'Joint\s*Venture\s*Agreement',
                r'certified\s*copy', r'municipal\s*account', r'Letter\s*of\s*Good\s*Standing'
            ]
            for pattern in gate_1_patterns:
                matches = re.findall(pattern, text, re.I)
                for m in set(matches):
                    clean_m = re.sub(r'[\n\r]', ' ', m).strip()
                    if clean_m.upper() not in [x.upper() for x in results["gate_1_mandatory"]]:
                        results["gate_1_mandatory"].append(clean_m)

            # 2. Gate 2 (Functional) - Improved point extraction
            # Look for explicit scoring markers
            weight_matches = re.findall(r'([A-Za-z\s]{5,50})\s+(\d{1,3})\s*points', text, re.I)
            if not weight_matches:
                 weight_matches = re.findall(r'([A-Za-z\s]{5,50})\s*(\d{1,3})\s*weight', text, re.I)

            # Catching table-style points (e.g., "Criterion ... 10")
            if not weight_matches:
                # Try finding lines that end with a number which is likely a score
                lines = text.split('\n')
                for line in lines:
                    m = re.search(r'^([A-Za-z\s]{5,50})\s+(\d{1,2})$', line.strip())
                    if m:
                        weight_matches.append(m.groups())

            for criterion, points in weight_matches:
                if int(points) > 0: # Avoid noise
                    results["gate_2_functional"].append({"criterion": criterion.strip(), "points": points})

            # 3. Pricing
            pp_match = re.search(r'(80/20|90/10)', text)
            if pp_match:
                results["pricing_preference"] = pp_match.group(1)

        return results
    except:
        return results

def generate_actionable_tasks(requirements):
    """Converts raw requirements into actionable, Jules-style tasks."""
    tasks = []

    mandatory = requirements.get("gate_1_mandatory", [])
    if mandatory:
        sbds = [m for m in mandatory if 'SBD' in m.upper() or 'MBD' in m.upper()]
        if sbds:
            tasks.append(f"Complete and sign all mandatory forms: {', '.join(sbds)} | 1")

        if any('CSD' in m.upper() for m in mandatory):
            tasks.append("Download and attach latest Full CSD Report (ensure MAAA is correct) | 1")

        if any('TAX' in m.upper() for m in mandatory):
            tasks.append("Verify Tax Compliance status on SARS and provide valid PIN | 1")

        if any('B-BBEE' in m.upper() for m in mandatory):
            tasks.append("Attach valid B-BBEE Certificate or correctly commissioned Sworn Affidavit | 1")

        if any('MUNICIPAL' in m.upper() for m in mandatory):
            tasks.append("Obtain recent municipal accounts (<90 days) for the Company and all Directors | 2")

    functional = requirements.get("gate_2_functional", [])
    if functional:
        # Sort by points descending and take top 2
        functional.sort(key=lambda x: int(x['points']), reverse=True)
        for item in functional[:2]:
            tasks.append(f"Draft detailed methodology addressing '{item['criterion']}' ({item['points']} pts) | 3")

        tasks.append("Gather Trinity of Evidence (Appointment, SLA, Completion) for previous projects | 2")

    if not tasks:
        tasks.append("Analyze Tender Documents for specific requirements | 1")
        tasks.append("Identify Mandatory Compliance items | 2")
        tasks.append("Prepare Initial Response Proposal | 3")

    return tasks[:5]

def update_tender_card(md_path, requirements):
    """Updates the AI Checklist section in the tender card."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    standard_comment = "<!-- This section is populated by Jules during enrichment. -->"
    tasks = generate_actionable_tasks(requirements)

    checklist = f"## AI Checklist (Jules)\n{standard_comment}\n"
    for task in tasks:
        checklist += f"- [ ] {task}\n"

    if "## AI Checklist (Jules)" in content:
        # Match from the header to the end of the file
        pattern = r"## AI Checklist \(Jules\)\s*\n<!--.*?-->.*"
        new_content = re.sub(pattern, checklist, content, flags=re.DOTALL)
        if new_content == content:
             new_content = re.sub(r"## AI Checklist \(Jules\).*", checklist, content, flags=re.DOTALL)
    else:
        new_content = content.strip() + "\n\n" + checklist

    with open(md_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

def process_file(md_file):
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        url_match = re.search(r'- \*\*Direct Link\*\*:\s*(https?://[^\s\n]+)', md_content)
        if not url_match: return False

        url = url_match.group(1).strip()
        if not url.lower().endswith(".pdf"): return False

        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            pdf_stream = io.BytesIO(resp.content)
            reqs = extract_requirements_from_pdf(pdf_stream)
            update_tender_card(md_file, reqs)
            return True
        return False
    except:
        return False

def main():
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    tender_dir = root / "03_tenders"

    # Support both flat and folder structures
    files = []
    for f in tender_dir.rglob("*.md"):
        if f.name in ["template.md", "registry_audit_log.md"] or f.name.endswith("_content.md"):
            continue
        # A file is a tender card if it's directly in 03_tenders or named {folder}.md inside a subfolder
        if f.parent == tender_dir or f.stem == f.parent.name:
            files.append(f)

    files.sort()

    print(f"Enriching {len(files)} tenders...")

    # Using 10 workers for speed but stability
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_file, files))

    print(f"Finished. Enriched {sum(results)} tenders.")

if __name__ == "__main__":
    main()
