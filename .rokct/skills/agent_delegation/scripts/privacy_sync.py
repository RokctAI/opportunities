# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
import hashlib
from pathlib import Path

def hash_recipients():
    """Hashes names and emails in recipient cards to protect privacy."""
    print("🔐 Processing Recipient Privacy Protection...")

    rec_dir = Path('.rokct/recipients')
    if not rec_dir.exists(): return

    for card_file in rec_dir.glob('*.md'):
        # Only process unhashed cards (they have email in filename or unhashed in content)
        with open(card_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already hashed (no [hash] markers)
        if "Subscription ID: " in content and "Leave blank" not in content:
            continue

        # Extract details
        name_match = re.search(r'-\s+\*\*Full Name\*\*:\s*(.+)$', content, re.MULTILINE)
        email_match = re.search(r'-\s+\*\*Email\*\*:\s*(.+)$', content, re.MULTILINE)

        if not name_match or not email_match: continue

        full_name = name_match.group(1).strip()
        email = email_match.group(1).strip()

        # Generate Hashes
        # We use a simple 8-char hash for the display but full for security
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:8]
        name_parts = full_name.split()
        surname = name_parts[-1] if name_parts else "User"
        first_name = name_parts[0] if name_parts else "Anon"

        sub_id = hashlib.sha256(f"{full_name}{email}".encode()).hexdigest()[:12]

        # Update Content
        # Hide full email and name details
        new_content = content.replace(f"Email**: {email}", f"Email**: [REDACTED]")
        new_content = new_content.replace(f"Subscription ID**: [Leave blank, will be hashed]", f"Subscription ID**: {sub_id}")

        # Rename File
        new_filename = f"{first_name}_{email_hash}_{surname}.{email_hash}.md"
        new_path = rec_dir / new_filename

        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Remove old file if it was plaintext
        if card_file.name != new_filename:
            os.remove(card_file)
            print(f"🔒 Hashed & Renamed: {card_file.name} -> {new_filename}")

if __name__ == "__main__":
    hash_recipients()
