# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
import hashlib
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from crypto_utils import encrypt_email

# Configuration
REC_DIR = Path('.rokct/recipients')
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def load_key():
    """Find and load encryption key from monorepo environment."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_path = os.path.join(project_root, ".env", "production.env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "EMAIL_ENCRYPTION_KEY=" in line:
                    return line.replace("export ", "").strip().split("=", 1)[1].strip("'\" ")
    
    return os.getenv('EMAIL_ENCRYPTION_KEY')

def process_privacy(check_only=False):
    """Enforces encryption-based privacy for recipient cards."""
    if not REC_DIR.exists():
        return True

    encryption_key = load_key()
    if not encryption_key and not check_only:
        print("❌ Error: EMAIL_ENCRYPTION_KEY not found. Cannot encrypt.")
        return False

    violations = []
    processed_count = 0
    
    print(f"🔐 {'Checking' if check_only else 'Applying'} Recipient Encryption Privacy...")

    for card_file in REC_DIR.glob('*.md'):
        filename = card_file.name
        with open(card_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Detection Logic
        has_raw_email_filename = bool(re.search(EMAIL_REGEX, filename))
        # Find raw email in content that isn't [REDACTED] or the template example
        found_emails = re.findall(EMAIL_REGEX, content)
        has_plaintext_email = any(e for e in found_emails if e.lower() != "email@example.com")
        
        # Check if filename is anonymous user_<hash>.md
        is_anonymous_filename = bool(re.match(r'^user_[a-f0-9]{12}\.md$', filename))

        if has_raw_email_filename or has_plaintext_email or not is_anonymous_filename:
            if check_only:
                violations.append(f"❌ Unencrypted PII in: {filename}")
                continue
            
            # 2. Encryption Logic
            email_match = re.search(r'-\s+\*\*Email\*\*:\s*(.+)$', content, re.MULTILINE)
            name_match = re.search(r'-\s+\*\*Full Name\*\*:\s*(.+)$', content, re.MULTILINE)
            
            if not email_match or not name_match:
                print(f"⚠️ Skipping {filename}: Missing mandatory Email or Full Name fields.")
                continue
                
            email = email_match.group(1).strip()
            full_name = name_match.group(1).strip()
            
            if email == "email@example.com": continue

            # Encrypt
            encrypted_blob = encrypt_email(email, encryption_key)
            
            # Generate anonymous identifier for filename
            display_hash = hashlib.sha256(email.lower().strip().encode()).hexdigest()[:12]
            sub_id = hashlib.sha256(f"{full_name}{email}".encode()).hexdigest()[:16]
            
            # Update Content
            new_content = content.replace(f"Full Name**: {full_name}", f"Full Name**: [REDACTED]")
            new_content = new_content.replace(f"Email**: {email}", f"Email**: [REDACTED]\n- **email_encrypted**: {encrypted_blob}")
            new_content = new_content.replace(f"Subscription ID**: [Leave blank, will be hashed]", f"Subscription ID**: {sub_id}")
            
            # Anonymize File
            new_filename = f"user_{display_hash}.md"
            new_path = REC_DIR / new_filename
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            if filename != new_filename:
                os.remove(card_file)
            
            print(f"🔒 Encrypted & Anonymized: {filename} -> {new_filename}")
            processed_count += 1

    if check_only:
        if violations:
            print("\n".join(violations))
            print("\n🚨 PRIVACY CHECK FAILED: Plaintext PII detected.")
            print("👉 Run 'python .rokct/skills/agent_delegation/scripts/privacy_sync.py' to encrypt.")
            return False
        print("✅ Privacy check passed. All emails are encrypted.")
        return True
    
    print(f"✅ Encryption sync complete. {processed_count} files secured.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enforce encryption-based privacy.")
    parser.add_argument("--check", action="store_true", help="Check for plaintext without modifying.")
    args = parser.parse_args()
    
    success = process_privacy(check_only=args.check)
    if not success:
        sys.exit(1)
