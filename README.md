# RokctAI Opportunities Registry

## 🚀 Registry Status Dashboard
*Last Updated: 2026-04-10 15:11*

| Registry | Total | New (7d) | Verified | Health |
| :--- | :--- | :--- | :--- | :--- |
| 🏦 **Equity** | 4 | 0 | 0 | 🟡 |
| 📜 **Grants** | 14 | 0 | 14 | 🟢 |
| 🏗️ **Tenders** | 0 | 0 | 0 | 🟢 |

**Overall Progress**: `77.8%` Verified | `+0` New Opportunities This Week
## Repository Structure

- **`01_equity/`**: Contains registries of potential funders and investment leads.
  - `funders.md`: A comprehensive list of VCs, Accelerators, and Corporate VCs.
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

-   **Adding Equity Leads**: Update the table in `01_equity/funders.md`.
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
