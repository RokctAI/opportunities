# eTenders OCDS Release Archive

The archive of every OCDS release published by the National Treasury
(South Africa) eTenders portal, fetched from
<https://ocds-api.etenders.gov.za> and kept current by the
[OCDS Archive Sync workflow](../.github/workflows/ocds-archive-sync.yml)
(`ocds/sync_ocds.py`).

**The data is not in git.** It lives in this repo's
[GitHub Releases](https://github.com/RokctAI/opportunities/releases),
overwritten in place on each sync, so the repository does not grow:

- `ocds-YYYY`, one release per year from 2021, holding that year's monthly
  shards. A year is a **pre-release** while it is running and becomes a
  full **release** once it has ended. Late awards are still added in place
  for 12 months after that.
- `ocds-index`, always a pre-release, holding `manifest.json`,
  `ocids.txt.gz` and the legacy / undated shards.

Download everything with:

```sh
for t in $(gh release list --limit 200 --json tagName -q '.[].tagName' | grep '^ocds-'); do
  gh release download "$t" --dir ocds-data
done
```

As of 2026-10-30: **168,670 releases**, tender IDs 1 to **176,377**,
real coverage April 2021 onward. `manifest.json` always has the live numbers.

## Contents of the release assets

- `releases-YYYY-MM.jsonl.gz` — one OCDS release JSON per line, gzipped,
  sharded by month of the release `date` field (from 2021-01), sorted by
  numeric tender ID.
- `releases-pre2021.jsonl.gz` — 234 legacy records with back-filled
  2009–2020 dates (and a few with year 0001).
- `releases-unknown-date.jsonl.gz` — records with no usable `date`.
- `manifest.json` — max ID, per-shard counts, empty-ID count, IDs pending
  retry, and stats from the last run.
- `ocids.txt.gz` — sorted list of every ocid in the archive.
- `buyers.json` — every buyer ever seen (keyed by lower-cased name), with
  its display name, tender count and the date it was first seen.

In git: `sync_ocds.py` (the sync script, Python stdlib only) and
`release_assets.sh` (moves the data to and from the release assets).

## Keeping it current

| Run | When | What it fetches |
| --- | --- | --- |
| Light | Tue + Fri, 02:00 UTC | New IDs since the last max, the top 300 IDs of the previous range, and IDs we hold no snapshot for |
| Full | 1st of each month, 03:00 UTC | Light, plus every release dated in the last 365 days (late awards / contracts) |

Run it by hand with `bash ocds/release_assets.sh download ocds-data`,
`python ocds/sync_ocds.py --archive-dir ocds-data [--refetch-days 365]`,
then `bash ocds/release_assets.sh upload ocds-data`, or trigger the
workflow manually.

## New-buyer alerts

Each sync compares the buyers in the archive against `buyers.json`. Any
buyer no earlier run has seen gets a GitHub issue titled "New eTenders
buyers detected (date)", listing the buyer, its tender count and links to
its releases. The first run only builds the index and opens nothing.
Matching is on the exact buyer name (whitespace- and case-normalised), so
a renamed department shows up as a new buyer.

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

Gzipped JSONL, about 50 MB in total (plain JSONL would be ~500 MB). Gzip
output is deterministic (fixed mtime, records sorted by ID), so a shard's
bytes change only when its content does, and each sync re-uploads only
the monthly shards that changed (largest ~1.2 MB; release assets allow up
to 2 GB each). The data was first committed to git in PR #100 (~50 MB of
history) and moved to release assets right after.

## Reading the archive

```python
import gzip, glob, json

for path in sorted(glob.glob("ocds-data/releases-*.jsonl.gz")):
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
