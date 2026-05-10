# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
from pathlib import Path

# Paths
BASE = Path('.')
WORKFLOWS = BASE / '.github' / 'workflows'

# Files to DELETE
TO_DELETE = [
    "agent-automated.yml", "agent-cleanup.yml", "registry-classification-sync.yml", 
    "registry-sync-excel.yml", "registry-sync.yml", "registry-weekly-report.yml", 
    "tender-sync.yml"
]

def cleanup():
    print("🧹 Starting Workflow Cleanup...")
    
    # 1. Delete Legacy Files
    for f in TO_DELETE:
        path = WORKFLOWS / f
        if path.exists():
            os.remove(path)
            print(f"  [-] Deleted: {f}")

    # 2. Create Universal Sync Engine
    engine_content = """# Copyright (c) 2026 RokctAI
name: "Opportunities: Universal Sync Engine"

on:
  schedule:
    - cron: '0 0 * * *' # Every night at midnight
  workflow_dispatch:

jobs:
  sync_and_orchestrate:
    runs-on: ubuntu-latest
    permissions: write-all
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install requests python-dotenv beautifulsoup4 lxml

      - name: 🏗️ Run Tender Engine (Sync)
        run: python .rokct/scripts/tenders/index.py

      - name: 🧹 Run Maintenance (Purge/Queue)
        run: python .rokct/scripts/maintenance/index.py

      - name: 📊 Run Registry Orchestrator (Dashboard/JSON/Todo)
        run: python .rokct/scripts/registry_orchestrator/index.py

      - name: 🚀 Commit and Push Updates
        run: |
          git config --global user.name "google-labs-jules[bot]"
          git config --global user.email "161369871+google-labs-jules[bot]@users.noreply.github.com"
          git add 03_tenders/*.md README.md published/api/meta.json .rokct/agent/todo.json 01_equity/*.md
          if git diff --staged --quiet; then
            echo "No changes to commit."
          else
            git commit -m "chore: nightly sync, metadata healing, and orchestration [skip ci]"
            git push origin main
          fi
"""
    with open(WORKFLOWS / 'sync-engine.yml', 'w', encoding='utf-8') as f:
        f.write(engine_content)
    print("✅ Created: sync-engine.yml")

    # 3. Kill Jekyll Error
    with open(BASE / '.nojekyll', 'w') as f:
        f.write("")
    print("✅ Created: .nojekyll (Killing Jekyll Ghost)")

if __name__ == "__main__":
    cleanup()
