# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path

# Comprehensive Country to ISO-3166-1 alpha-2 mapping
ISO_MAP = {
    "india": "IN", "south africa": "ZA", "usa": "US", "united states": "US",
    "united kingdom": "GB", "uk": "GB", "global": "GLOBAL", "nigeria": "NG",
    "kenya": "KE", "brazil": "BR", "germany": "DE", "france": "FR",
    "canada": "CA", "australia": "AU", "china": "CN", "japan": "JP",
    "israel": "IL", "egypt": "EG", "mexico": "MX", "spain": "ES",
    "italy": "IT", "netherlands": "NL", "sweden": "SE", "norway": "NO",
    "denmark": "DK", "finland": "FI", "switzerland": "CH", "austria": "AT",
    "belgium": "BE", "portugal": "PT", "greece": "GR", "turkey": "TR",
    "russia": "RU", "singapore": "SG", "malaysia": "MY", "thailand": "TH",
    "indonesia": "ID", "philippines": "PH", "vietnam": "VN", "south korea": "KR",
    "argentina": "AR", "chile": "CL", "colombia": "CO", "peru": "PE",
    "uae": "AE", "saudi arabia": "SA", "qatar": "QA", "ghana": "GH"
}

def heal_equity_flags(file_path, content):
    """Automatically injects missing Flag metadata into Equity cards."""
    # Check if flag already exists
    if re.search(r'-\s+\*\*Flag\*\*:', content):
        return content

    # 1. Extract Country
    country_match = re.search(r'-\s+\*\*Country\*\*:\s*(.*)', content, re.I)
    if not country_match:
        return content

    country_raw = country_match.group(1).strip()
    country_key = country_raw.lower()
    
    # 2. Map to Flag (Look for partial matches too)
    flag = "GLOBAL"
    for name, code in ISO_MAP.items():
        if name in country_key:
            flag = code
            break
    
    # 3. Inject Flag after Country
    print(f"  🚩 Healing Equity Flag: {file_path.name} ({country_raw} -> {flag})")
    new_line = f"\n- **Flag**: {flag}"
    
    # Inject right after the Country line
    content = re.sub(r'(-\s+\*\*Country\*\*:[^\n]+)', r'\1' + new_line, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content
