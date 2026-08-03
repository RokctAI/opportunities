# TenderAssist v2 — Pillar 1 Brief: Model-Read-and-Verify Requirements Extraction

**Status:** Revised scoping brief awaiting owner sign-off. v2 direction and pillars 2–4 are
owner-approved; this pillar's earlier framing was rejected (see Framing correction) and this
revision replaces it.
**Decision trail:** `agent/decision_log.md` (TenderAssist ADR) and
`agent/replay/docs/supacharge-open-decisions-log.md` #26.

## Framing correction (owner review, 2026-08-02)

The previous revision pitched this pillar as "genuinely Fable-agentic, not a drop-in model
swap." The owner rejected that claim, and on inspection the rejection is correct — it is
retracted, not restated. The design below is **one structured-output model call per tender
plus a deterministic Python grounding check**: an extraction *pipeline* (single-LLM-call
tier), not an agentic loop, and nothing in it is vendor- or model-specific. The documents are
small (~5–50KB of text), so long-context capability is irrelevant; the "self-verification" was
deliberately moved *out* of the model into string matching; any capable model runs the
identical script. What Jules/regex lacks and this adds is simply model *reading comprehension*
over the full document — which many models provide. Accordingly this brief is
model-agnostic, and **which model runs it is a measured cost/quality decision made during the
canary bake-off**, not an architecture choice made up front.

## Goal

Replace the regex core of the tender enrichment pipeline with a model-read-and-verify
extraction step that reads each tender's full document text and produces a complete, verified
compliance checklist. This fixes the product-blocking coverage gap (only ~2 of 517 currently published
tenders have any checklist; the 443 enriched entries in `meta.json` are historical) while
raising checklist quality from "regex keyword hits, capped at 5 tasks" to a genuine
requirements matrix. **The output contract does not change** — cards still get an
`## AI Checklist (Jules)` block, the orchestrator still publishes `meta.json`
`advanced_enrichment` from cards, and the v1 backend/frontend consume it unchanged.

## Current pipeline (verified, all paths relative to `opportunities/`)

1. `registry_orchestrator/index.py` scans `03_tenders/` cards. Cards with a real
   `## AI Checklist (Jules)` block → published into `meta.json.advanced_enrichment`
   (`scanners.py:94`, `updaters.py:78`). Cards without → queued in `.rokct/agent/todo.json`.
2. The enrichment worker ("Jules") consumes `todo.json`:
   - `scripts/tenders/enrichment/pdf_to_md.py` — downloads the card's Direct Link PDF,
     extracts text with pdfplumber → `{id}_content.md`.
   - `scripts/tenders/enrichment/extract_requirements.py` — **the part being replaced**:
     regex over the PDF text for SBD/MBD forms, CSD, tax, B-BBEE, COIDA (`gate_1_mandatory`),
     weighted criteria (`gate_2_functional`), 80/20 vs 90/10; `generate_actionable_tasks()`
     caps at 5 tasks with generic fallbacks; writes the card's AI Checklist block.
3. Sizing (measured 2026-08-02): 517 published tenders, **all 517 have a Direct Link PDF**,
   only 1 has `{id}_content.md` — so each run is stage 1 (existing PDF→text) + stage 2 (new).

## Design

### Shape: batch pipeline script, not an interactive agent

A Python script in the existing enrichment folder (working name
`extract_requirements_ai.py`), same CLI contract as the file it replaces: consume
`todo.json`, write card blocks, log failures. It uses the plain `anthropic` SDK — no
Managed Agents, no sandbox, no tool loop: one extraction call per tender, then deterministic
post-processing. Non-latency-sensitive → **Message Batches API** (50% price cut, results
within ~1h, poll → collect keyed by `custom_id` = tender slug).

### Model call (per tender)

- **Model: a config value, decided by the canary bake-off** (see Rollout). Candidates:
  `claude-sonnet-5` ($3/$15 per MTok), `claude-opus-5` ($5/$25), `claude-fable-5` ($10/$50).
  Given the doc sizes and the deterministic grounding gate downstream, the working hypothesis
  is that Sonnet- or Opus-tier is sufficient; a more expensive model earns its place only if
  the bake-off shows a grounded-accuracy delta worth the price. Per-model request config
  (thinking/effort params differ across models) is an implementation detail of the config,
  not of the pipeline.
- **Input:** the tender card (metadata) + `{id}_content.md` full text. Median doc is small
  (~5–50KB text); no chunking needed on any candidate model.
- **Output:** structured outputs (`output_config.format`, `json_schema`) — guaranteed-valid
  JSON requirements matrix:

```
{
  "mandatory_documents":   [{"name", "detail", "source_quote"}],   // SBD/MBD forms, CSD, tax PIN, B-BBEE, COIDA, JV, deposits…
  "eligibility_thresholds":[{"requirement", "source_quote"}],      // CIDB grading, registrations, minimum experience
  "functional_criteria":   [{"criterion", "weight", "source_quote"}],
  "pricing_preference":    "80/20" | "90/10" | "unknown",
  "briefing":              {"compulsory": bool, "detail", "source_quote"} | null,
  "submission":            {"method", "copies", "sealing/labeling detail", "source_quote"} | null,
  "confidence":            "high" | "medium" | "low"               // model's own assessment of doc completeness/legibility
}
```

### Grounding check (the anti-hallucination gate, deterministic and free)

Every extracted item must carry a `source_quote` — a verbatim snippet from the document.
The script then verifies **in Python** that each quote actually appears in the source text
(normalized whitespace). Items whose quotes fail are dropped and logged. This converts
"trust the model" into "trust string matching": no second model call needed for
verification, and a tender whose items all fail grounding falls back to the generic
2-task block rather than publishing fabricated requirements. (A Fable re-try pass for
failed items is a later optimization, not v1 of this pipeline.)

### Task generation

Grounded matrix → ordered card tasks, in Python (not another model call): mandatory docs
first ("Complete and sign: SBD 4, SBD 6…"), then thresholds, then functional/methodology
tasks with their weights, then briefing/submission logistics. Keep the established
`"task text | N"` format (N = weight) so `Bid Checklist Item.weight` parsing in `control`
keeps working. Lift the 5-task cap to ~10 (the cap was a regex-quality workaround; real
matrices legitimately have 8–10 items). Also write the full grounded matrix to
`{id}_requirements.json` next to the card — additive sidecar, not yet published, ready to
feed pillars 2–3 without re-extraction.

### Failure & refusal handling

- PDF unreachable / not text-extractable → existing failure log
  (`.rokct/agent/logs/pdf_extraction_failures.log` pattern); card keeps generic block.
- `stop_reason == "refusal"` (safety classifiers on Fable/Opus-5-tier models; unlikely on
  procurement text but must be handled — check before reading `content`): log, fall back to
  generic block. Server-side `fallbacks` is rejected on the Batches API, so refused items
  simply retry once via the regular API on an older-tier model before falling back.
- Any tender the pipeline can't enrich gets the generic block — **never** fabricated tasks,
  and never a silent skip that leaves the card queued forever.
- Idempotent by construction: the orchestrator only queues cards without a real checklist;
  re-runs skip enriched cards (same behavior as today's `VERIFIED` skip).

### Cost envelope (estimate at ~10K input + ~2K output tokens per tender, Batches pricing)

| Model | Per tender | Backfill (517) | Steady state (~10–30/day) |
|---|---|---|---|
| `claude-sonnet-5` | ~$0.03 | ~$16 | ~$0.30–1/day |
| `claude-opus-5` | ~$0.05 | ~$26 | ~$0.50–1.50/day |
| `claude-fable-5` | ~$0.10 | ~$50–60 | ~$1–3/day |

All are small enough that the decision should be made on measured grounded accuracy, not
price — but the table shows there is no cost case for the expensive model unless it wins on
quality.

## Rollout

1. **Canary bake-off (this is also the model decision):** the same 20 tenders (spread across
   provinces/types) run through the identical script on each candidate model. Compare:
   grounded-item count per tender (items surviving the quote check), owner spot-check
   accuracy against the PDFs, and measured cost/tender. Pick the cheapest model that isn't
   measurably worse; record the decision and numbers in the product log.
2. **Backfill:** full current catalog; orchestrator republishes `meta.json`; verify the v1
   detail page renders real checklists and `advanced_available` counts jump.
3. **Recurring:** wire into whatever runs the orchestrator today so new tenders enrich on
   sync. **Open question for owner:** where does/should this run (the repo publishes via
   GitHub — Actions with an API-key secret? the VPS?). Only if the bake-off selects
   `claude-fable-5`: confirm the org meets its 30-day data-retention requirement (ZDR orgs
   get 400s on every call).

## Acceptance criteria

- ≥ 80% of current tenders with a reachable, text-extractable PDF carry an ADVANCED
  checklist after backfill (measured: enriched ÷ published).
- 100% of published checklist items pass the grounding check (enforced by construction).
- Canary spot-check: no fabricated mandatory documents in 20/20 reviewed tenders; missed
  requirements noted and tolerated at this stage (regex misses nearly everything today).
- `meta.json` schema byte-compatible for existing consumers; v1 backend tests still pass.
- Model choice justified by bake-off numbers (grounded accuracy + cost), recorded in the
  product log; cost/tender within 2× of the chosen model's estimate above.

## Non-goals (this brief only)

Pillars 2–4 (bid/no-bid, audit, drafting); publishing `{id}_requirements.json` into the
API (sidecar only for now); fixing the public-GitHub paywall gap (separate prereq, already
logged); any change to `meta.json` schema or the v1 code.
