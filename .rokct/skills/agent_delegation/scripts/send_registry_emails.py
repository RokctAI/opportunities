# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

def send_registry_emails():
    # Robust Path & Env Handling
    # We calculate the root directory by climbing up from this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_path = os.path.join(project_root, ".env", "production.env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
        # Aggressive Manual Fallback for Monorepo-fetched files
        required_keys = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']
        if not all(os.environ.get(k) for k in required_keys):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.replace("export ", "").strip().split("=", 1)
                        os.environ[key.strip()] = val.strip("'\" ")
    else:
        load_dotenv()
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    
    recipient_dir = Path(project_root) / '.rokct' / 'recipients'
    published_dir = Path(project_root) / 'published'
    
    if not recipient_dir.exists():
        print("No recipients found. Skipping.")
        return

    # Check for weekly updates
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    # We still fetch the main files
    updates = {
        'Equity': [f for f in published_dir.glob('01_Equity_*.xlsx') if datetime.fromtimestamp(f.stat().st_mtime) > week_ago],
        'Grants': [f for f in published_dir.glob('02_Grants_*.xlsx') if datetime.fromtimestamp(f.stat().st_mtime) > week_ago],
        'Tenders': [f for f in published_dir.glob('03_Tenders_*.xlsx') if datetime.fromtimestamp(f.stat().st_mtime) > week_ago]
    }

    # For Privacy/Monorepo setup: Real emails are stored in Monorepo secrets or a secure database.
    # In this workflow, we assume the PR process handles the actual mapping or use a lookup.
    # RULE: For this implementation, we will look for an unhashed backup or a mapping file.
    # Since we Redacted them for safety, the actual sending requires the real email list
    # which should be in MONOREPO_PAT secured storage.

    # MOCK MAPPING (In production, this would be fetched from Monorepo Secrets)
    email_mapping = {}

    for card in recipient_dir.glob('*.md'):
        with open(card, 'r') as f:
            content = f.read()
            
        # Parse Subscriptions
        attachments = []
        if "### Tenders\n- **Subscribed**: Yes" in content:
            attachments.extend(updates['Tenders'])
        if "### Grants\n- **Subscribed**: Yes" in content:
            attachments.extend(updates['Grants'])
        if "### Equity\n- **Subscribed**: Yes" in content:
            attachments.extend(updates['Equity'])
            
        # Find real email if available
        # Note: If redacted, we need the Monorepo PAT to fetch the unredacted map
        # For now, we process if an email is found or logged.
        email_match = re.search(r'-\s+\*\*Email\*\*:\s*(.+)$', content, re.MULTILINE)
        if email_match and "[REDACTED]" not in email_match.group(1):
            email = email_match.group(1).strip()
            if attachments:
                send_email(email, attachments, smtp_server, smtp_port, smtp_user, smtp_pass)
                print(f"✅ Sent weekly update to {email}")

def send_email(to_email, files, server, port, user, password):
    msg = MIMEMultipart()
    msg['From'] = f"RokctAI Registry <{user}>"
    msg['To'] = to_email
    msg['Subject'] = f"📂 Weekly Registry Update: {datetime.now().strftime('%Y-%m-%d')}"
    
    body = "Hi,\n\nPlease find the latest filtered opportunity reports attached based on your subscriptions.\n\nBest,\nRokctAI Agent"
    msg.attach(MIMEText(body, 'plain'))
    
    for f_path in files:
        with open(f_path, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=f_path.name)
            part['Content-Disposition'] = f'attachment; filename="{f_path.name}"'
            msg.attach(part)
            
    use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
            
    with smtplib.SMTP(server, port) as server:
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.send_message(msg)

if __name__ == "__main__":
    send_registry_emails()