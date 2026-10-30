# eTenders OCDS Release Archive

The archive of every OCDS release published by the National Treasury
(South Africa) eTenders portal, fetched from
<https://ocds-api.etenders.gov.za> and kept current by the
[OCDS Archive Sync workflow](../.github/workflows/ocds-archive-sync.yml)
(`ocds/sync_ocds.py`).

As of 2026-10-30: **168,670 releases**, tender IDs 1 to **176,377**,
real coverage April 2021 onward. `manifest.json` always has the live numbers.

## Contents

- `releases-YYYY-MM.jsonl.gz` — one OCDS release JSON per line, gzipped,
  sharded by month of the release `date` field (from 2021-01), sorted by
  numeric tender ID.
- `releases-pre2021.jsonl.gz` — 234 legacy records with back-filled
  2009–2020 dates (and a few with year 0001).
- `releases-unknown-date.jsonl.gz` — records with no usable `date`.
- `manifest.json` — max ID, per-shard counts, empty-ID count, IDs pending
  retry, and stats from the last run.
- `ocids.txt.gz` — sorted list of every ocid in the archive.
- `sync_ocds.py` — the sync script (Python stdlib only).

## Keeping it current

| Run | When | What it fetches |
| --- | --- | --- |
| Light | Tue + Fri, 02:00 UTC | New IDs since the last max, the top 300 IDs of the previous range, and IDs we hold no snapshot for |
| Full | 1st of each month, 03:00 UTC | Light, plus every release dated in the last 365 days (late awards / contracts) |

Run it by hand with `python ocds/sync_ocds.py [--refetch-days 365]`.

## Completeness: the honest exceptions

- **Empty IDs** (~4,000): IDs that return "not found" — never published or
  removed. Unheld IDs near the top are re-checked each run in case they
  were allocated before publication.
- **Pending-retry IDs**: the API returns persistent, deterministic HTTP 500
  for some records. On 2026-10-30 this hit ~45% of recently published IDs,
  including ~3,700 new IDs we have no snapshot of yet (so most current
  `03_tenders/` cards are not in the archive yet). Every run retries them;
  a failure never overwrites a snapshot we already hold.
- **Late awards**: releases are compiled snapshots that gain `awards` /
  `contracts` blocks over time. They land on the next full run; awards on
  releases older than 365 days are not re-fetched.
- **Removed releases**: if the API stops serving a release we already
  hold, the archive keeps the last snapshot.

## Why ID enumeration, not the list endpoint

The list endpoint (`/api/OCDSReleases?dateFrom=..&dateTo=..`) has unstable
offset pagination: the same date window returns different subsets across
page sizes and runs, silently dropping records (verified 2026-08-20). The
archive enumerates the sequential ID space instead, via
`GET /api/OCDSReleases/release/ocds-9t57fa-{N}`, which is deterministic.

## Format choice

Gzipped JSONL. Plain JSONL would be ~10× larger (~500 MB vs ~50 MB) and
every sync would add that much more to git history. Gzip output is
deterministic (fixed mtime, records sorted by ID), so a shard's bytes
change only when its content does, and monthly shards (largest ~1.2 MB,
far under GitHub's 50 MB warning) keep each sync's rewrite small.

## Reading the archive

```python
import gzip, glob, json

for path in sorted(glob.glob("ocds/releases-*.jsonl.gz")):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            release = json.loads(line)
```

## Joining to `03_tenders/`

Tender cards in [`03_tenders/`](../03_tenders) are named by ocid
(`03_tenders/ocds-9t57fa-<N>.md` or `03_tenders/ocds-9t57fa-<N>/`), and
the card's `Tender Number` bullet holds the same ocid. Join that to each
archive line's `ocid` field; `tender.id` holds the bare numeric ID. Check
`manifest.json` `pending_retry_ids` for cards that have no archive record
yet.

Tender document PDFs are not stored; each release lists its document URLs
under `tender.documents[].url`, which download without auth.
