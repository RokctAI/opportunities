# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import re
from pathlib import Path
from datetime import datetime

def update_audit_logs():
    """Ensures all registry directories have up-to-date audit logs."""
    print("📝 Updating Registry Audit Logs...")

    dirs = {
        '01_equity': 'LIVING',
        '02_grants': 'STATIC',
        '03_tenders': 'LIVING'
    }

    for dir_path, mode in dirs.items():
        directory = Path(dir_path)
        if not directory.exists(): continue

        log_path = directory / 'registry_audit_log.md'

        total_rows = 0
        verified_rows = 0

        for f in directory.glob('*.md'):
            if f.name in ['template.md', 'registry_audit_log.md', 'global_audit_log.md']: continue
            total_rows += 1
            with open(f, 'r', encoding='utf-8') as content:
                if "VERIFIED" in content.read():
                    verified_rows += 1

        # Check if file exists to preserve history or create new
        # For simplicity in this task, we recreate it with current state
        log_content = f"""# Registry Audit Log: {dir_path.split('_')[1].capitalize()}

| File Path | Mode | Status | Last Audit Date | Verified Rows | Total Rows |
| :--- | :--- | :--- | :--- | :--- | :--- |
| {dir_path}/ | {mode} | { 'COMPLETE' if verified_rows == total_rows and total_rows > 0 else 'IN_PROGRESS' } | {datetime.now().strftime('%Y-%m-%d')} | {verified_rows} | {total_rows} |

## Recent Changes
- Automated audit log update: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Verified: {verified_rows}/{total_rows} ({ (verified_rows/total_rows*100) if total_rows > 0 else 0 :.1f}%)
"""
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        print(f"✅ Updated audit log for {dir_path}")

if __name__ == "__main__":
    update_audit_logs()
