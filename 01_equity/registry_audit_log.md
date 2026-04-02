# Registry Audit Log
This file tracks the verification status of files in the `opportunities/01_equity/` directory.
| File Path | Mode | Status | Last Audit Date | Verified Rows | Total Rows | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| opportunities/01_equity/funders.md | STATIC | COMPLETE | 2026-03-13 | 60 | 60 | Archived (Rolled over to Part 2). |
| opportunities/01_equity/funders_2026_part2.md | STATIC | COMPLETE | 2026-03-13 | 200 | 200 | Reached 200 row limit, marked STATIC. |
| opportunities/01_equity/funders_2026_part3.md | STATIC | COMPLETE | 2026-04-02 | 200 | 200 | Reached 200 row limit, marked STATIC. |
| opportunities/01_equity/funders_2026_part4.md | LIVING | IN_PROGRESS | 2026-04-02 | 42 | 42 | Newly created rollover file. |

## Instructions for Agent
1. Scan the `opportunities/01_equity/` directory daily.
2. For each file NOT marked as **COMPLETE** in this log:
   - Audit all rows for missing names, emails, or citations.
   - Strictly follow anti-hallucination rules (No placeholders, mandatory citations).
   - Once a file has 100% verified sources for all rows, update its status to **COMPLETE**.
3. **ISOLATION**: Explicitly IGNORE the `opportunities/published/` folder.
4. **AUTO-DISCOVERY**: If you find new `.md` files in `01_equity/`, add them to this log.