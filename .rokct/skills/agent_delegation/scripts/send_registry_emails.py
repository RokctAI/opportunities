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
from crypto_utils import decrypt_email

def load_environment():
    """Robust environment loading with aggressive manual fallback."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_path = os.path.join(project_root, ".env", "production.env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.replace("export ", "").strip().split("=", 1)
                    if not os.environ.get(key.strip()):
                        os.environ[key.strip()] = val.strip("'\" ")
    else:
        load_dotenv()
    return project_root

def send_registry_emails():
    project_root = load_environment()
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    encryption_key = os.getenv('EMAIL_ENCRYPTION_KEY')

    if not encryption_key:
        print("❌ EMAIL_ENCRYPTION_KEY not found. Cannot send emails.")
        return
    
    recipient_dir = Path(project_root) / '.rokct' / 'recipients'
    published_dir = Path(project_root) / 'published'
    
    if not recipient_dir.exists():
        print("No recipients found. Skipping.")
        return

    # Check for weekly updates
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    # 1. Map new Opportunities to their Classifications
    # This allows us to only send users the items that match their cards
    registry_map = {
        'Equity': [],
        'Grants': [],
        'Tenders': []
    }

    # Helper: Extract classifications from a tender markdown
    def get_tender_meta(f_path):
        with open(f_path, 'r') as f:
            text = f.read()
            cat = re.search(r'### Category\s*\n\s*(.+)', text)
            inst = re.search(r'-\s+\*\*Institution\*\*:\s*(.+)$', text, re.MULTILINE)
            t_type = re.search(r'-\s+\*\*Tender Type\*\*:\s*(.+)$', text, re.MULTILINE)
            return {
                'file': f_path,
                'category': cat.group(1).strip() if cat else "",
                'institution': inst.group(1).strip() if inst else "",
                'type': t_type.group(1).strip() if t_type else ""
            }

    # Gather new items from this week
    for f in (Path(project_root) / '03_tenders').glob('*.md'):
        if f.name in ['template.md', 'registry_audit_log.md'] or datetime.fromtimestamp(f.stat().st_mtime) < week_ago: continue
        registry_map['Tenders'].append(get_tender_meta(f))

    for f in (Path(project_root) / '02_grants').glob('*.md'):
        if f.name in ['template.md', 'registry_audit_log.md'] or datetime.fromtimestamp(f.stat().st_mtime) < week_ago: continue
        registry_map['Grants'].append({'file': f})

    for f in (Path(project_root) / '01_equity').glob('*.md'):
        if f.name in ['template.md', 'registry_audit_log.md', 'global_audit_log.md'] or datetime.fromtimestamp(f.stat().st_mtime) < week_ago: continue
        registry_map['Equity'].append({'file': f})
    
    # Check for weekly update reports (The Excel/PDF files)
    report_updates = {
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
        if card.name == 'template_card.md': continue
        with open(card, 'r') as f:
            content = f.read()
            
        # 2. Parse Granular Subscriptions
        attachments = []
        
        # TENDERS MATCHING
        if "### Tenders\n- **Subscribed**: Yes" in content:
            # Look for configurations: Category: [X] | Organ of State: [Y] | Tender Type: [Z]
            configs = re.findall(r'Configuration \d+: Category: (.*?) \| Organ of State: (.*?) \| Tender Type: (.*)', content)
            
            for item in registry_map['Tenders']:
                match_found = False
                for c_cat, c_inst, c_type in configs:
                    # Check if tender matches ANY of the user's configurations
                    # We allow partial/keyword matching for robustness
                    if (c_cat.lower() in item['category'].lower() or c_cat == "[e.g., Construction]") and \
                       (c_inst.lower() in item['institution'].lower() or c_inst == "[e.g., ESKOM]") and \
                       (c_type.lower() in item['type'].lower() or c_type == "[e.g., Request for Quotation]"):
                        match_found = True
                        break
                
                if match_found:
                    # Logic: If it matches a specific new tender, we send the Master Report
                    # but only if it matches their filter.
                    # For now, we attach the master if ANY match is found.
                    if report_updates['Tenders']:
                        attachments.extend(report_updates['Tenders'])
                        break

        # GRANTS MATCHING
        if "### Grants\n- **Subscribed**: Yes" in content:
            if report_updates['Grants']:
                attachments.extend(report_updates['Grants'])

        # EQUITY MATCHING
        if "### Equity\n- **Subscribed**: Yes" in content:
            if report_updates['Equity']:
                attachments.extend(report_updates['Equity'])
            
        # REVERSIBLE PRIVACY: Decrypt the stored email blob
        email_encrypted_match = re.search(r'-\s+\*\*email_encrypted\*\*:\s*(.+)$', content, re.MULTILINE)
        
        if email_encrypted_match:
            encrypted_blob = email_encrypted_match.group(1).strip()
            try:
                real_email = decrypt_email(encrypted_blob, encryption_key)
                if attachments:
                    send_email(real_email, attachments, smtp_server, smtp_port, smtp_user, smtp_pass)
                    print(f"✅ Sent weekly update to REDACTED_USER ({card.name})")
            except Exception as e:
                print(f"❌ Failed to decrypt email for {card.name}: {e}")

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