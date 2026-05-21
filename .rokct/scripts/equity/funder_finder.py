import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import sys

# Identify project root
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / '.rokct').exists():
    BASE_DIR = BASE_DIR.parent

# Mocking FunderManager for local call if needed
sys.path.append(str(BASE_DIR / '.rokct' / 'scripts' / 'equity'))
from funder_manager import FunderManager

def find_candidates(url):
    manager = FunderManager(registry_path=str(BASE_DIR / '01_equity'))
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        candidates = []

        # Look for numbers followed by dot in h2 or other elements
        # Failory uses <h2>1. <a ...>Name</a></h2>
        for h2 in soup.find_all(['h2', 'h3']):
            text = h2.get_text().strip()
            match = re.search(r'^\d+\.\s+(.*)', text)
            if match:
                name = match.group(1).strip()
                if not manager.is_duplicate(name):
                    candidates.append(name)

        # Fallback: look for common patterns if nothing found
        if not candidates:
            for item in soup.find_all(['li', 'strong']):
                text = item.get_text().strip()
                if 3 < len(text) < 50 and re.match(r'^[A-Z0-9]', text):
                    if not manager.is_duplicate(text):
                        candidates.append(text)

        return list(set(candidates))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []
