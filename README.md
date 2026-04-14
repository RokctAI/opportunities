# RokctAI Opportunities Registry

## 🚀 Registry Status Dashboard
*Last Updated: 2026-04-14 11:11*

| Registry | Total | New (7d) | Verified | Health |
| :--- | :--- | :--- | :--- | :--- |
| 🏦 **Equity** | 664 | 664 | 0 | 🟡 |
| 📜 **Grants** | 14 | 14 | 14 | 🟢 |
| 🏗️ **Tenders** | 309 | 309 | 0 | 🟡 |

**Overall Progress**: `1.4%` Verified | `+987` New Opportunities This Week | [🌐 View Live Dashboard](https://rokctai.github.io/Opportunities-Registry/)
## Repository Structure

- **`01_equity/`**: Individual markdown cards for potential funders and investment leads, following `template.md`.
- **`02_grants/`**: Individual markdown files for grant opportunities, following the `template.md`.
- **`03_tenders/`**: Individual markdown files for tender opportunities, primarily synced from the South African eTenders portal.
- **`published/`**: Automatically generated Excel files (.xlsx) for easier distribution and consumption.
- **`.rokct/`**: Contains automation scripts and agent-related configurations.

## Automation & Workflows

The repository uses GitHub Actions to automate several tasks:

1.  **Tender Sync (`.github/workflows/tender-sync.yml`)**: Periodically fetches new tenders from the South African eTenders OCDS API and updates the `03_tenders/` directory.
2.  **Excel Sync (`.github/workflows/registry-sync-excel.yml`)**: Triggered on pushes to the registry directories. It converts the markdown data into styled Excel files located in `published/`.
    -   **Note**: Only "Verified" or "ACTIVE" entries are included in the published Excel files.
3.  **Weekly Report (`.github/workflows/registry-weekly-report.yml`)**: Sends a summary report of new and active opportunities every Friday.
4.  **Agent Delegation (`.github/workflows/agent-automated.yml`)**: Processes a task queue for AI-driven automation tasks.

## How to Contribute

-   **Adding Equity Leads**: Create a new `.md` file in `01_equity/` using `01_equity/template.md` as a guide.
-   **Adding Grants**: Create a new `.md` file in `02_grants/` using `02_grants/template.md` as a guide.
-   **Verifying Data**: Ensure that entries have a `Status: ACTIVE` or are otherwise marked as verified to be included in the public exports.

### 🔐 Privacy Protection
This repository enforces strict PII (Personally Identifiable Information) protection for all recipient cards.
- **Enforcement**: CI will fail if raw emails or human-readable names are found in `.rokct/recipients/`.
- **Local Fix**: Run `python .rokct/skills/agent_delegation/scripts/privacy_sync.py` to anonymize your card before committing.
- **Pre-commit**: We recommend installing pre-commit hooks (`pre-commit install`) to handle this automatically.

## Technical Details

-   **Languages**: Python (for sync scripts), YAML (for workflows).
-   **Dependencies**: `pandas`, `openpyxl`, `requests`, `python-dotenv`.
-   **Secrets**: The repository fetches environment configurations from the central `RokctAI/Monorepo` to ensure consistency across the ecosystem.
