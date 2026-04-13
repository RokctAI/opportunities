# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import json
from pathlib import Path
from datetime import datetime, timedelta

HISTORICAL_LOG = Path('.rokct/agent/logs/historical_opportunities.json')

def track_historical_data():
    """Records closing dates of opportunities to predict future occurrences."""
    print("📈 Tracking Historical Opportunity Lifecycle...")

    dirs = [Path('01_equity'), Path('02_grants'), Path('03_tenders')]
    history = {}

    if HISTORICAL_LOG.exists():
        with open(HISTORICAL_LOG, 'r') as f:
            history = json.load(f)

    today = datetime.now()
    updated = False

    for directory in dirs:
        if not directory.exists(): continue
        for f in directory.glob('*.md'):
            if f.name in ['template.md', 'registry_audit_log.md']: continue

            with open(f, 'r', encoding='utf-8') as content:
                text = content.read()

                # Extract Title and Date
                import re
                title_match = re.search(r'^# (?:Tender Opportunity|Grant Opportunity|Equity Opportunity):?\s*(.*)', text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f.stem

                closing_match = re.search(r'-\s+\*\*Closing Date\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
                if closing_match:
                    closing_date = closing_match.group(1)

                    if title not in history:
                        history[title] = []

                    if closing_date not in history[title]:
                        history[title].append(closing_date)
                        updated = True

    if updated:
        HISTORICAL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORICAL_LOG, 'w') as f:
            json.dump(history, f, indent=2)
        print(f"✅ Updated historical log with {len(history)} unique opportunities.")
    else:
        print("ℹ️ No new historical data to record.")

    generate_predictive_alerts(history)

def generate_predictive_alerts(history):
    """Analyzes history to find opportunities likely to reopen soon."""
    alerts = []
    today = datetime.now()

    for title, dates in history.items():
        for date_str in dates:
            try:
                prev_date = datetime.strptime(date_str, '%Y-%m-%d')
                # If it's a yearly opportunity, check if the anniversary is in 2 months
                next_expected = prev_date.replace(year=today.year)

                # If already passed this year, look at next year
                if next_expected < today:
                    next_expected = next_expected.replace(year=today.year + 1)

                days_until = (next_expected - today).days
                if 30 <= days_until <= 60:
                    alerts.append({
                        'title': title,
                        'expected_date': next_expected.strftime('%Y-%m-%d'),
                        'days_until': days_until
                    })
            except:
                continue

    if alerts:
        alert_file = Path('.rokct/agent/logs/predictive_alerts.md')
        with open(alert_file, 'w') as f:
            f.write("# 🔔 Predictive Opportunity Alerts\n\n")
            f.write("The following opportunities are predicted to reopen based on historical cycles (Yearly).\n\n")
            f.write("| Opportunity | Predicted Reopen | Lead Time |\n")
            f.write("| :--- | :--- | :--- |\n")
            for a in alerts:
                f.write(f"| {a['title']} | {a['expected_date']} | {a['days_until']} days |\n")
        print(f"📢 Generated {len(alerts)} predictive alerts.")

if __name__ == "__main__":
    track_historical_data()
