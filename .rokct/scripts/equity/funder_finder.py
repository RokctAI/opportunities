import re
import requests
from bs4 import BeautifulSoup
from funder_manager import FunderManager
import sys

def find_candidates(url):
    manager = FunderManager()
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Heuristic: look for list items or table cells that look like names
        potential_names = []

        # Check list items
        for li in soup.find_all('li'):
            text = li.get_text().strip()
            if 3 < len(text) < 50:
                potential_names.append(text)

        # Check table cells
        for td in soup.find_all('td'):
            text = td.get_text().strip()
            if 3 < len(text) < 50:
                potential_names.append(text)

        # Check links
        for a in soup.find_all('a'):
            text = a.get_text().strip()
            if 3 < len(text) < 50:
                potential_names.append(text)

        unique_candidates = sorted(list(set(potential_names)))

        new_candidates = []
        for name in unique_candidates:
            if not manager.is_duplicate(name):
                new_candidates.append(name)

        return new_candidates
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 funder_finder.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    new_ones = find_candidates(url)
    print(f"Found {len(new_ones)} potential new funders:")
    for name in new_ones[:50]:
        print(f"- {name}")
