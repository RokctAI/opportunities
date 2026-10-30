#!/usr/bin/env python3
# Copyright (c) 2026 ROKCT INTELLIGENCE (PTY) LTD
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Sync the South African eTenders OCDS release archive.

Keeps ocds/releases-*.jsonl.gz current against the National Treasury OCDS API
(https://ocds-api.etenders.gov.za) by sequential tender-ID enumeration:

  GET /api/OCDSReleases/release/ocds-9t57fa-{N}

The list endpoint (/api/OCDSReleases?dateFrom=..) is deliberately NOT used:
its offset pagination is unstable and silently drops records (verified
2026-08-20: the same date window returned different subsets across page
sizes and runs). Single-release lookups are deterministic.

Each run:
  1. Probes upward from the last known max ID to find the current max
     (binary search on the 404 boundary, then a linear margin scan, because
     unpublished/removed IDs also return 404 and can sit near the top).
  2. Fetches all new IDs since the last run.
  3. Re-fetches IDs in the recent window (--refetch-days, default 365):
     releases are compiled snapshots, so awards/contracts/amendments appear
     on old IDs only when re-fetched.
  4. Retries IDs that previously failed with HTTP 500. The API returns
     persistent, deterministic 500s for a varying subset of records
     (server-side; observed 2026-10-30 at ~40% of recent IDs). A 500 never
     overwrites an existing snapshot; the ID goes to manifest
     pending_retry_ids and is retried on every later run.
  5. Rewrites only the shards whose content changed, with deterministic
     gzip (mtime=0, level 9, records sorted by numeric ID) so unchanged
     shards stay byte-identical and create no git churn.

Response classification:
  200 + JSON  -> stored (replaces any previous snapshot of that ID)
  200 + {}    -> empty (never published / removed); recorded, not stored
  404         -> empty (same meaning; the API switched from `{}` to 404
                 for unpublished IDs some time after 2026-08)
  500 (final) -> pending retry; existing snapshot (if any) is kept

Usage:
  python ocds/sync_ocds.py [--refetch-days 365] [--concurrency 12]
                           [--archive-dir ocds] [--dry-run]
"""

import argparse
import concurrent.futures as cf
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://ocds-api.etenders.gov.za/api/OCDSReleases/release/ocds-9t57fa-{n}"
PREFIX = "ocds-9t57fa-"
# 500s are deterministic per ID (server-side record corruption), so long
# in-run retry loops just burn hours; failed IDs are retried on later runs.
RETRIES = 3
BACKOFF = 1.0  # seconds, doubled each retry
TIMEOUT = 60
# Consecutive 404s above a candidate max before we accept it. Gaps of
# >1,700 consecutive unpublished IDs exist below the live max (seen
# 2026-10-30 around ID 168k), so this must be generous.
MAX_PROBE_MARGIN = 5000
# IDs are allocated before they are published, so the top of the previous
# run's range is re-checked for IDs that were empty then.
TOP_RECHECK = 300


def log(msg):
    print(msg, flush=True)


def fetch_one(n):
    """Return (n, status, body) where status in {ok, empty, fail}."""
    url = API.format(n=n)
    delay = BACKOFF
    last_err = "unknown"
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read()
            text = body.decode("utf-8", "replace").strip()
            if not text or text == "{}":
                return n, "empty", None
            try:
                json.loads(text)
            except ValueError:
                last_err = "bad-json"
                time.sleep(delay)
                delay *= 2
                continue
            return n, "ok", text
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return n, "empty", None
            if e.code == 500:
                # Deterministic per ID; retrying in-run never helps.
                return n, "fail", "http-500"
            last_err = "http-%d" % e.code
        except Exception as e:  # noqa: BLE001 - network errors of all kinds
            last_err = type(e).__name__
        time.sleep(delay)
        delay *= 2
    return n, "fail", last_err


def probe_status(n):
    """Cheap existence probe: ok/fail (both mean a record is there) or empty.

    No retry loop for 500s — a single 500 already proves the ID exists.
    """
    url = API.format(n=n)
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                text = resp.read().decode("utf-8", "replace").strip()
            return "empty" if (not text or text == "{}") else "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "empty"
            return "fail"
        except Exception:  # noqa: BLE001
            time.sleep(1)
    return "empty"


def probe_max(start, pool):
    """Find the highest existing ID at or above `start`."""
    # Grow an upper bound by doubling the step until a window is all-empty.
    lo = start
    step = 4096
    while True:
        cand = lo + step
        # Wide sampled window: unpublished-ID gaps below the max span 1,700+.
        if any_exists(cand, cand + 2000, pool, samples=40):
            lo = cand
            step *= 2
        else:
            break
    # Margin scan above the candidate; repeat until a full margin is empty.
    while True:
        found = scan_exists(lo + 1, lo + MAX_PROBE_MARGIN, pool)
        if found is None:
            return lo
        lo = found


def any_exists(a, b, pool, samples=8):
    ids = list(range(a, b + 1))
    stepped = ids[:: max(1, len(ids) // samples)][:samples]
    results = pool.map(probe_status, stepped)
    return any(st in ("ok", "fail") for st in results)


def scan_exists(a, b, pool):
    """Highest existing ID in [a, b], or None."""
    best = None
    ids = list(range(a, b + 1))
    for n, st in zip(ids, pool.map(probe_status, ids)):
        if st in ("ok", "fail"):
            best = n if best is None else max(best, n)
    return best


def shard_name(date_str):
    """Monthly shards from 2021 (when the platform starts); one shard for the
    ~200 back-filled legacy records. Small monthly files keep each sync's
    rewrites (and so git history growth) to the months that actually changed."""
    if not date_str or len(date_str) < 7:
        return "releases-unknown-date.jsonl.gz"
    year, month = date_str[:4], date_str[5:7]
    if not (year.isdigit() and month.isdigit() and 1 <= int(month) <= 12):
        return "releases-unknown-date.jsonl.gz"
    if int(year) < 2021:
        return "releases-pre2021.jsonl.gz"
    return "releases-%s-%s.jsonl.gz" % (year, month)


def numeric_id(ocid):
    try:
        return int(ocid.rsplit("-", 1)[1])
    except (ValueError, IndexError):
        return -1


def read_shard(path):
    """Return {numeric_id: (ocid, date, raw_line)}."""
    out = {}
    if not os.path.exists(path):
        return out
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            ocid = rec.get("ocid", "")
            out[numeric_id(ocid)] = (ocid, rec.get("date") or "", line)
    return out


def write_shard(path, records, dry_run):
    """Deterministic gzip: sorted by ID, mtime=0, level 9. Returns True if file changed."""
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
        for n in sorted(records):
            gz.write(records[n][2].encode("utf-8"))
            gz.write(b"\n")
    new_bytes = buf.getvalue()
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read() == new_bytes:
                return False
    if not dry_run:
        with open(path, "wb") as f:
            f.write(new_bytes)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--archive-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--refetch-days", type=int, default=365)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--max-id", type=int, default=0,
                    help="skip probing and use this max ID")
    ap.add_argument("--start-id", type=int, default=0,
                    help="re-check every unheld ID from here up (default: last max - %d)" % TOP_RECHECK)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    adir = args.archive_dir
    manifest_path = os.path.join(adir, "manifest.json")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    old_max = int(manifest["max_id_probed"])
    # The original 2026-08 one-shot fetch counted 3,147 empty IDs without
    # listing them; that count is kept as a base and new empties are listed.
    empty_base = int(manifest.get("empty_id_base", manifest.get("empty_id_count", 0)))
    empty_ids = set(manifest.get("new_empty_ids", []))
    pending = set(manifest.get("pending_retry_ids", manifest.get("failed_ids", [])))

    cutoff = time.strftime("%Y-%m-%d", time.gmtime(time.time() - args.refetch_days * 86400))
    log("archive dir: %s" % adir)
    log("last max ID: %d | refetch cutoff date: %s" % (old_max, cutoff))

    # Load all shards once; we need dates to pick the refetch window, and the
    # full set to rewrite any shard a record moves into or out of.
    shards = {}  # name -> {n: (ocid, date, line)}
    for name in sorted(os.listdir(adir)):
        if name.startswith("releases-") and name.endswith(".jsonl.gz"):
            shards[name] = read_shard(os.path.join(adir, name))
    total_before = sum(len(s) for s in shards.values())
    log("loaded %d releases from %d shards" % (total_before, len(shards)))

    # Re-home any record not in the shard its date maps to (layout changes).
    changed_names = set()
    for name in list(shards):
        for n, rec in list(shards[name].items()):
            target = shard_name(rec[1][:10])
            if target != name:
                del shards[name][n]
                shards.setdefault(target, {})[n] = rec
                changed_names.update((name, target))

    id_to_shard = {}
    refetch = set()
    for name, recs in shards.items():
        for n, (_, date, _) in recs.items():
            id_to_shard[n] = name
            if args.refetch_days > 0 and date[:10] >= cutoff:
                refetch.add(n)

    # IDs with no snapshot at all are always retried; failed re-fetches of
    # IDs we already hold only on runs that re-fetch the window.
    retry = {n for n in pending if n not in id_to_shard or args.refetch_days > 0}

    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        new_max = args.max_id or probe_max(old_max, pool)
        log("current max ID: %d (%d new IDs)" % (new_max, max(0, new_max - old_max)))

        start = args.start_id or max(1, old_max - TOP_RECHECK)
        todo = sorted(
            {n for n in range(start, new_max + 1) if n not in id_to_shard}
            | refetch
            | {n for n in retry if n <= new_max}
        )
        log("fetching %d IDs (%d new, %d refetch window, %d pending retries)"
            % (len(todo), max(0, new_max - old_max), len(refetch), len(retry)))

        stats = {"ok": 0, "empty": 0, "fail": 0}
        fetched = {}  # n -> (ocid, date, line)
        failed_now = set()
        done = 0
        for n, status, payload in pool.map(fetch_one, todo):
            done += 1
            if done % 2000 == 0:
                log("  ... %d/%d (ok=%d empty=%d fail=%d)"
                    % (done, len(todo), stats["ok"], stats["empty"], stats["fail"]))
            stats[status] += 1
            if status == "ok":
                rec = json.loads(payload)
                fetched[n] = (rec.get("ocid", PREFIX + str(n)), rec.get("date") or "", payload)
                pending.discard(n)
                empty_ids.discard(n)
            elif status == "empty":
                pending.discard(n)
                # Keep an existing snapshot: 'empty' on a previously published
                # ID means removed from the API, and this is an archive.
                if n not in id_to_shard:
                    empty_ids.add(n)
            else:
                failed_now.add(n)

    log("fetch done: ok=%(ok)d empty=%(empty)d fail=%(fail)d" % stats)

    # Merge into shards.
    for n, (ocid, date, line) in fetched.items():
        target = shard_name(date[:10])
        prev = id_to_shard.get(n)
        if prev and prev != target:
            del shards[prev][n]
            changed_names.add(prev)
        shards.setdefault(target, {})
        if shards[target].get(n, (None, None, None))[2] != line:
            shards[target][n] = (ocid, date, line)
            changed_names.add(target)
        id_to_shard[n] = target

    wrote = []
    for name in sorted(changed_names):
        path = os.path.join(adir, name)
        if not shards.get(name):
            shards.pop(name, None)
            if os.path.exists(path):
                if not args.dry_run:
                    os.remove(path)
                wrote.append(name + " (removed)")
            continue
        if write_shard(path, shards[name], args.dry_run):
            wrote.append(name)
    log("shards changed: %s" % (", ".join(wrote) if wrote else "none"))

    # ocids.txt.gz (sorted, deterministic).
    all_ids = sorted(id_to_shard)
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
        for n in all_ids:
            gz.write((PREFIX + str(n) + "\n").encode("ascii"))
    ocids_path = os.path.join(adir, "ocids.txt.gz")
    if not args.dry_run:
        old = open(ocids_path, "rb").read() if os.path.exists(ocids_path) else b""
        if old != buf.getvalue():
            with open(ocids_path, "wb") as f:
                f.write(buf.getvalue())

    pending = {n for n in (pending | failed_now) if n not in fetched}
    total_after = sum(len(s) for s in shards.values())
    manifest.update({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "sequential tender-ID enumeration via /api/OCDSReleases/release/ocds-9t57fa-{N}",
        "max_id_probed": new_max,
        "unique_release_count": total_after,
        "raw_release_count": total_after,
        "empty_id_base": empty_base,
        "new_empty_ids": sorted(empty_ids),
        "empty_id_count": empty_base + len(empty_ids),
        "pending_retry_ids": sorted(pending),
        "pending_retry_count": len(pending),
        "refetch_days": args.refetch_days,
        "last_run": {
            "fetched_ok": stats["ok"],
            "empty": stats["empty"],
            "failed": stats["fail"],
            "ids_attempted": len(todo),
        },
        "shards": {
            name: {"release_count": len(recs),
                   "bytes_gz": os.path.getsize(os.path.join(adir, name))
                   if os.path.exists(os.path.join(adir, name)) else 0}
            for name, recs in sorted(shards.items()) if recs
        },
    })
    # Legacy keys from the original one-shot fetch no longer apply.
    for k in ("progress_next_id", "batches_done", "resume", "complete",
              "completion_note", "started", "finished", "failed_ids",
              "failed_id_count", "fetch_batch_size", "curl_parallel_max"):
        manifest.pop(k, None)
    if not args.dry_run:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1)
            f.write("\n")

    log("archive now holds %d releases (was %d); max ID %d; %d IDs pending retry"
        % (total_after, total_before, new_max, len(pending)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
