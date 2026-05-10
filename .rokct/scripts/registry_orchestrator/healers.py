# Licensed under the MIT License.
# Copyright 2024 RokctAI

import re
from pathlib import Path

# Full Comprehensive ISO Mapping
ISO_MAP = {
    "afghanistan": "AF", "albania": "AL", "algeria": "DZ", "andorra": "AD", "angola": "AO",
    "argentina": "AR", "armenia": "AM", "australia": "AU", "austria": "AT", "azerbaijan": "AZ",
    "bahamas": "BS", "bahrain": "BH", "bangladesh": "BD", "barbados": "BB", "belarus": "BY",
    "belgium": "BE", "belize": "BZ", "benin": "BJ", "bhutan": "BT", "bolivia": "BO",
    "bosnia": "BA", "botswana": "BW", "brazil": "BR", "bulgaria": "BG", "burkina faso": "BF",
    "burundi": "BI", "cambodia": "KH", "cameroon": "CM", "canada": "CA", "cape verde": "CV",
    "central african republic": "CF", "chad": "TD", "chile": "CL", "china": "CN", "colombia": "CO",
    "comoros": "KM", "congo": "CG", "costa rica": "CR", "croatia": "HR", "cuba": "CU",
    "cyprus": "CY", "czech republic": "CZ", "denmark": "DK", "djibouti": "DJ", "dominica": "DM",
    "dominican republic": "DO", "ecuador": "EC", "egypt": "EG", "el salvador": "SV",
    "equatorial guinea": "GQ", "eritrea": "ER", "estonia": "EE", "eswatini": "SZ",
    "ethiopia": "ET", "fiji": "FJ", "finland": "FI", "france": "FR", "gabon": "GA",
    "gambia": "GM", "georgia": "GE", "germany": "DE", "ghana": "GH", "greece": "GR",
    "grenada": "GD", "guatemala": "GT", "guinea": "GN", "guyana": "GY", "haiti": "HT",
    "honduras": "HN", "hungary": "HU", "iceland": "IS", "india": "IN", "indonesia": "ID",
    "iran": "IR", "iraq": "IQ", "ireland": "IE", "israel": "IL", "italy": "IT",
    "jamaica": "JM", "japan": "JP", "jordan": "JO", "kazakhstan": "KZ", "kenya": "KE",
    "kiribati": "KI", "korea": "KR", "kuwait": "KW", "kyrgyzstan": "KG", "laos": "LA",
    "latvia": "LV", "lebanon": "LB", "lesotho": "LS", "liberia": "LR", "libya": "LY",
    "liechtenstein": "LI", "lithuania": "LT", "luxembourg": "LU", "madagascar": "MG",
    "malawi": "MW", "malaysia": "MY", "maldives": "MV", "mali": "ML", "malta": "MT",
    "marshall islands": "MH", "mauritania": "MR", "mauritius": "MU", "mexico": "MX",
    "micronesia": "FM", "moldova": "MD", "monaco": "MC", "mongolia": "MN", "montenegro": "ME",
    "morocco": "MA", "mozambique": "MZ", "myanmar": "MM", "namibia": "NA", "nauru": "NR",
    "nepal": "NP", "netherlands": "NL", "new zealand": "NZ", "nicaragua": "NI", "niger": "NE",
    "nigeria": "NG", "north macedonia": "MK", "norway": "NO", "oman": "OM", "pakistan": "PK",
    "palau": "PW", "panama": "PA", "papua new guinea": "PG", "paraguay": "PY", "peru": "PE",
    "philippines": "PH", "poland": "PL", "portugal": "PT", "qatar": "QA", "romania": "RO",
    "russia": "RU", "rwanda": "RW", "saint kitts": "KN", "saint lucia": "LC", "samoa": "WS",
    "san marino": "SM", "saudi arabia": "SA", "senegal": "SN", "serbia": "RS", "seychelles": "SC",
    "sierra leone": "SL", "singapore": "SG", "slovakia": "SK", "slovenia": "SI", "solomon islands": "SB",
    "somalia": "SO", "south africa": "ZA", "south sudan": "SS", "spain": "ES", "sri lanka": "LK",
    "sudan": "SD", "suriname": "SR", "sweden": "SE", "switzerland": "CH", "syria": "SY",
    "taiwan": "TW", "tajikistan": "TJ", "tanzania": "TZ", "thailand": "TH", "timor-leste": "TL",
    "togo": "TG", "tonga": "TO", "trinidad": "TT", "tunisia": "TN", "turkey": "TR",
    "turkmenistan": "TM", "tuvalu": "TV", "uganda": "UG", "ukraine": "UA", "uae": "AE",
    "united arab emirates": "AE", "united kingdom": "GB", "uk": "GB", "usa": "US",
    "united states": "US", "uruguay": "UY", "uzbekistan": "UZ", "vanuatu": "VU",
    "vatican city": "VA", "venezuela": "VE", "vietnam": "VN", "yemen": "YE", "zambia": "ZM",
    "zimbabwe": "ZW"
}

def heal_equity_flags(file_path, content):
    """Automatically injects missing Flag metadata with priority matching."""
    if re.search(r'-\s+\*\*Flag\*\*:', content):
        return content

    country_match = re.search(r'-\s+\*\*Country\*\*:\s*(.*)', content, re.I)
    if not country_match:
        return content

    country_raw = country_match.group(1).strip()
    country_key = country_raw.lower()
    
    flag = "GLOBAL"
    # Check specific countries in order of dictionary (Python 3.7+)
    for name, code in ISO_MAP.items():
        if name in country_key:
            flag = code
            break
            
    if flag == "GLOBAL" and "global" in country_key:
        flag = "GLOBAL"
    
    print(f"  🚩 Healing Equity Flag: {file_path.name} ({country_raw} -> {flag})")
    new_line = f"\n- **Flag**: {flag}"
    content = re.sub(r'(-\s+\*\*Country\*\*:[^\n]+)', r'\1' + new_line, content, count=1)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content
