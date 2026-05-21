# Licensed under the MIT License.
# Copyright 2026 RokctAI

import os
import re
import urllib.parse
from pathlib import Path
from datetime import datetime
import requests

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / '.rokct').exists():
    BASE_DIR = BASE_DIR.parent

TARGET_REGISTRIES = [
    BASE_DIR / "01_equity",
    BASE_DIR / "02_grants",
    BASE_DIR / "04_eeip"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_definitive_dead(url):
    """
    Tests a URL and returns a tuple (is_dead, reason, status_code).
    WAF/IP blocks (403, 429) or transient SSL/timeout issues are NOT considered definitive dead links.
    Definitive dead links are 404 Not Found, DNS failure, or connection refused.
    """
    try:
        # Use GET with stream=True so we only fetch headers and don't download large payloads
        response = requests.get(url, headers=HEADERS, timeout=12, stream=True)
        
        status = response.status_code
        if status == 404:
            return True, "Definitive 404 Not Found", status
        
        # 400 Bad Request, 410 Gone might also be considered dead, 
        # but 403 Forbidden / 429 Too Many Requests are WAF blocks on CI runners.
        if status == 410:
            return True, "Definitive 410 Gone", status
            
        if status in [401, 403, 429]:
            # This is a soft block/WAF issue in GitHub VMs
            return False, f"WAF / Bot Mitigation Block (Soft Warning)", status
            
        return False, "Live / Accessible", status
        
    except requests.exceptions.ConnectionError as ce:
        # Check if it's a DNS resolution failure
        err_str = str(ce).lower()
        if "name or service not known" in err_str or "failed to resolve" in err_str or "gaierror" in err_str or "nosuchhost" in err_str:
            return True, "DNS Name Resolution Failure", None
        if "connection refused" in err_str:
            return True, "Connection Refused", None
        return False, f"Connection Error (Soft Warning: {type(ce).__name__})", None
        
    except requests.exceptions.Timeout:
        return False, "Connection Timeout (Soft Warning)", None
    except requests.exceptions.SSLError:
        return False, "SSL Verification Error (Soft Warning)", None
    except Exception as e:
        return False, f"Unknown Error (Soft Warning: {type(e).__name__})", None

def check_and_update_card(path):
    """Parses a markdown card, extracts links, tests them, and downgrades status if dead."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Skip files that don't have verification status
    if "Verification Status**:" not in content:
        return False

    # Extract all link fields using regex
    # Matches patterns like: - **Apply Link**: http://... or - **Source**: http://...
    link_fields = re.findall(r'-\s*\*\*(Website|Applying Link|Apply Link|Source|Source / Verification)\*\*:\s*(https?://[^\s\)]+)', content)
    
    if not link_fields:
        return False

    is_downgraded = False
    downgrade_reason = ""
    dead_url = ""

    for field, url in link_fields:
        url = url.strip()
        # Skip placeholders or relative file paths (e.g. 04_eeip/sources/...)
        if not url.startswith("http"):
            continue
            
        is_dead, reason, status_code = is_definitive_dead(url)
        if is_dead:
            is_downgraded = True
            downgrade_reason = reason
            dead_url = url
            break  # Any definitive dead link triggers a downgrade

    if is_downgraded:
        # Find existing status
        status_match = re.search(r'(Verification Status\*\*:\s*)(VERIFIED|IN_PROGRESS|UNVERIFIED)', content)
        if status_match and status_match.group(2) != "UNVERIFIED":
            # Upgrade status to UNVERIFIED
            content = re.sub(
                r'Verification Status\*\*:\s*(VERIFIED|IN_PROGRESS)',
                'Verification Status**: UNVERIFIED',
                content
            )
            # Update Last Verified date
            today = datetime.now().strftime('%Y-%m-%d')
            content = re.sub(
                r'Last Verified\*\*:\s*[^\n]+',
                f'Last Verified**: {today}',
                content
            )
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"⚠️ [DOWNGRADED] {path.relative_to(BASE_DIR)} due to: {downgrade_reason} ({dead_url})")
            return True
        else:
            # Already unverified, no change needed but log it
            print(f"ℹ️ [Dead Link (Already Unverified)] {path.relative_to(BASE_DIR)}: {dead_url} ({downgrade_reason})")
            
    return False

def main():
    print("==================================================")
    # Print header
    print("Opportunities Registry Resilient CI Link Checker")
    print("==================================================")
    
    total_scanned = 0
    total_downgraded = 0
    
    for registry_dir in TARGET_REGISTRIES:
        if not registry_dir.exists():
            continue
            
        print(f"\nScanning registry: {registry_dir.name}...")
        for card_file in registry_dir.rglob("*.md"):
            fname = card_file.name.lower()
            if fname in ['template.md', 'readme.md', 'registry_audit_log.md'] or fname.startswith('registry_'):
                continue
                
            total_scanned += 1
            try:
                did_downgrade = check_and_update_card(card_file)
                if did_downgrade:
                    total_downgraded += 1
            except Exception as e:
                print(f"  [Error processing] {card_file.name}: {e}")
                
    print("\n==================================================")
    print("CI Link Audit Summary:")
    print(f"  Total Cards Scanned: {total_scanned}")
    print(f"  Total Cards Downgraded to UNVERIFIED: {total_downgraded}")
    print("==================================================")

if __name__ == "__main__":
    main()
