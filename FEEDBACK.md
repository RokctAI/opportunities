# RokctAI Opportunities Registry: Features & Improvements Feedback

This document outlines suggested features and improvements for the Opportunities Registry based on an analysis of current infrastructure and user feedback.

## 1. AI-Driven Automation & Enrichment

### 1.1 Deep Document Parsing (Jules v2) [DONE - Musina]
*   **Status**: ✅ **DONE** for Musina municipality; pending integration into `tender_sync_api.py`.
*   **Feature**: Enhance enrichment tasks to download and OCR/analyze PDF attachments (e.g., SBD forms, TORs).
*   **Recommendation**: Use specialized Python libraries (like `PyMuPDF` or `pdfplumber`) to minimize hallucinations during extraction.
*   **Impact**: Extract "Mandatory Requirements" (B-BBEE level, tax compliance) and "Evaluation Criteria" with high accuracy.

### 1.2 Automated Suitability Scoring [DONE]
*   **Status**: ✅ **DONE**. Implemented in the tender SDK (RokctAI/corporate `tender/frappe`): deterministic 0-100 fit score with strong/possible/poor/ineligible bands via the `get_tender_suitability` gateway endpoint, scoring this registry's published cards against the user's Tender Business Profile (hard eligibility gates incl. CIDB grading, compliance-rule coverage, sector/geography fit, functionality-threshold demand). No AI - fixture rules and whitelisted extraction only.
*   **Feature**: Implement a scoring algorithm that compares opportunity requirements against a user-provided "Business Profile".
*   **Impact**: Prioritize opportunities based on specific business competencies.

### 1.3 Multi-Source Expansion (API + Scraping) [DONE]
*   **Status**: ✅ **DONE**. Initial implementation for Musina Local Municipality completed (`musina_sync.py`).
*   **Feature**: Expand beyond the South African eTenders API to regional and municipal portals.
*   **Target**: Implement web scrapers for other municipalities (e.g., following the Musina WordPress pattern).
*   **Impact**: Increases the coverage of localized government opportunities not always listed on the national eTenders portal.

## 2. Data Integrity & Health

### 2.1 Lychee-Powered Link Monitoring [DONE]
*   **Status**: ✅ **DONE**. Integrated via `.github/workflows/universal-links.yml`.
*   **Feature**: Integrate results from the `lychee-action` (Universal Link Checker) directly into the registry health dashboard.
*   **Impact**: Automatically flag and update the status of markdown files to `BROKEN` when links (sources or application URLs) fail.

### 2.2 Versioned Audit Logs [DONE]
*   **Status**: ✅ **DONE**. Standardized `registry_audit_log.md` implemented in each directory.
*   **Feature**: Formalize the `registry_audit_log.md` to include a summary of *what* changed (e.g., "Updated Deadline", "Added AI Analysis").
*   **Impact**: Full traceability for both manual steward updates and automated syncs.

## 3. User Experience & Accessibility

### 3.1 Interactive Dashboard & Self-Service [REJECTED]
*   **Status**: ❌ **REJECTED**. Replaced by high-priority GitHub Pages implementation.
*   **Feature**: Transition from a static README to a lightweight web dashboard (e.g., GitHub Pages).

### 3.2 "Application Tracking" Workflow [REJECTED]
*   **Status**: ❌ **REJECTED**.
*   **Feature**: Use GitHub Issues or a dedicated log file to track the progress of applications for specific opportunities.

## 4. Strategic Analytics & Alerts

### 4.1 Predictive Opportunity Alerts [DONE]
*   **Status**: ✅ **DONE**. Historical tracking logic implemented.
*   **Feature**: Implement a "Historical Opportunity Log" that tracks when recurring grants or long-term tender contracts were previously opened.
*   **Proactive Notification**: Send alerts (e.g., 2 months in advance) for recurring opportunities (e.g., "This grant opened in June last year; prepare your documents now"), even if the previous file was deleted.
*   **Impact**: Moves from reactive discovery to proactive preparation.

### 4.2 Competitive Intelligence [DONE - Musina]
*   **Status**: ✅ **DONE** for Musina municipality (`musina_bids_intelligence.log`).
*   **Feature**: Extract "Awarded To" data and contract periods (e.g., 5-year contracts) from documents.
*   **Lifecycle Monitoring**: If a tender has a fixed period, flag it for re-evaluation 6 months before the contract is set to expire.

## 5. Maintenance & Standards

### 5.1 Repository Hygiene [DONE]
*   **Status**: ✅ **DONE**. `.gitignore` updated to exclude `*.pyc` and `__pycache__/`.

---
*Prepared by Jules (AI Senior Engineer)*
*Date: 2026-04-12*
