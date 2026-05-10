# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path

# Common Country to ISO Flag mapping
COUNTRY_MAP = {
    "india": "IN",
    "south africa": "ZA",
    "usa": "US",
    "united states": "US",
    "uk": "GB",
    "united kingdom": "GB",
    "global": "GLOBAL",
    "nigeria": "NG",
    "kenya": "KE",
    "brazil": "BR"
}

def heal_equity_flags(file_path, content):
    """Automatically injects missing Flag metadata into Equity cards based on Country."""
    if "- **Flag**:" in content:
        return content # Already has a flag

    # 1. Extract Country
    country_match = re.search(r'-\s+\*\*Country\*\*:\s*(.*)', content, re.I)
    if not country_match:
        return content # No country to base a flag on

    country_name = country_match.group(1).strip().lower()
    
    # 2. Map to Flag
    flag = COUNTRY_MAP.get(country_name, "GLOBAL") # Default to GLOBAL if unknown
    
    # 3. Inject Flag after Country
    print(f"  🚩 Healing Equity Flag: {file_path.name} ({country_name} -> {flag})")
    new_line = f"\n- **Flag**: {flag}"
    # Inject right after the Country line
    content = re.sub(r'(-\s+\*\*Country\*\*:[^\n]+)', r'\1' + new_line, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content
