# Licensed under the MIT License.
import sys
from pathlib import Path
from datetime import datetime

# Add internal paths to sys.path
sys.path.append(str(Path(__file__).parent / 'api'))
sys.path.append(str(Path(__file__).parent / 'scrapers'))

import ocds
import musina

BASE_DIR = Path(__file__).parent.parent.parent.parent
TENDER_DIR = BASE_DIR / '03_tenders'
SOURCES_DIR = TENDER_DIR / 'sources'

def generate_md(release, flag, source_ref):
    # (Shared Markdown Generation Logic)
    return f"# Tender {release.get('ocid')}\n- Flag: {flag}\n- Source: {source_ref}"

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] --- Tender Database Sync ---")
    ocds.run_sync(TENDER_DIR, SOURCES_DIR, generate_md)
    musina.run_sync(TENDER_DIR, SOURCES_DIR, generate_md)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync Complete.")
