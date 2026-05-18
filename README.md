# RokctAI Opportunities Registry

## 🚀 Registry Status Dashboard
*Last Updated: 2026-05-18 05:07*

| Registry | Total | New (7d) | Verified | Health |
| :--- | :--- | :--- | :--- | :--- |
| 🏦 **Equity** | 881 | 881 | 881 | 🟢 |
| 📜 **Grants** | 201 | 201 | 201 | 🟢 |
| 🏗️ **Tenders** | 600 | 600 | 600 | 🟢 |

**Overall Progress**: `100.0%` Verified | `+1682` New Opportunities This Week | [🌐 View Live Dashboard](https://rokctai.github.io/Opportunities-Registry/)
## Repository Structure

- **`01_equity/`**: Individual markdown cards for potential funders and investment leads.
- **`02_grants/`**: Individual markdown files for grant opportunities.
- **`03_tenders/`**: Individual markdown files for tender opportunities (Scraped from OCDS).
- **`published/api/`**: Single source of truth JSON API for the Next.js frontend.
- **`.rokct/scripts/`**: Modularized automation engine (Sync, Maintenance, Orchestration).

## Automation & Workflows

The repository uses a **Universal Sync Engine** (`.github/workflows/sync-engine.yml`) to manage the pipeline:

1.  **Weekly Sync (Mondays)**: Performs heavy OCDS and Musina scraping to find new opportunities.
2.  **Maintenance**: Purges closed tenders and generates the weekly `todo.json` for Jules.
3.  **Fast Refresh (On Push)**: Triggered by manual edits. Heals metadata (Flags/Verified) and instantly regenerates the JSON API.

## How to Contribute

-   **Adding Equity/Grants**: Use the `template.md` in the respective folders.
-   **Multi-Tag Filtering**: Use slashes (`/`) in fields like Industry or Territory to add multiple tags (e.g., `Tech / Fintech`).
-   **Flags**: Add a `- **Country**: India` line, and the bot will automatically inject the `- **Flag**: IN` line for you.

### 🔐 Privacy Protection
This repository enforces strict PII protection for all recipient cards.
- **Enforcement**: CI will fail if raw emails or human-readable names are found in `.rokct/recipients/`.
- **Local Fix**: Run `python .rokct/scripts/privacy/index.py` to anonymize your card before committing.

## Technical Details

-   **Backend**: Python 3.10+
-   **Database**: Git-as-a-Database (Markdown + JSON API).
-   **Frontend Integration**: The Next.js app consumes `published/api/meta.json` for all data.
