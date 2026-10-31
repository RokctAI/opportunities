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
"""New-buyer issues: one GitHub issue per new buyer, with a living Part A.

Lifecycle (labels on the issue, which stays open throughout):
  new-buyer + needs-quirks   opened by this script; Part A comment posted
  profile-pr-open            set by Part B once a corporate profile PR exists
  closed                     when that profile PR merges

Part A is the data half of a buyer profile, built from the OCDS archive with
no AI: tender counts, categories, methods, bid windows, awards, suppliers,
contacts. One comment per issue, marked with PART_A_MARK, rewritten in place
on every sync while the issue is open; when the tender count changes a dated
line is appended under "Updates". Part B (the quirks from the tender packs)
is out of scope here.

Usage (needs gh authenticated for the repo; GITHUB_REPOSITORY set):
  python ocds/buyer_issues.py --archive-dir ocds-data --new-buyers new_buyers.json
"""

import argparse
import collections
import json
import os
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_ocds  # noqa: E402

BUYER_MARK = "<!-- ocds-buyer: %s -->"
PART_A_MARK = "<!-- ocds-part-a -->"
COUNT_MARK = "<!-- ocds-part-a-tenders: %d -->"
LABELS = {
    "new-buyer": ("0e8a16", "Buyer first seen by the OCDS Archive Sync"),
    "needs-quirks": ("fbca04", "Part A posted; Part B (pack quirks) pending"),
    "profile-pr-open": ("1d76db", "Corporate buyer-profile PR is open"),
}
RELEASE_URL = "https://ocds-api.etenders.gov.za/api/OCDSReleases/release/%s"


def gh(*args, input_text=None):
    out = subprocess.run(["gh", *args], input=input_text, capture_output=True,
                         text=True, check=True)
    return out.stdout


def gh_json(*args):
    text = gh(*args)
    return json.loads(text) if text.strip() else None


def records_by_buyer(adir):
    by = collections.defaultdict(list)
    for name in sorted(os.listdir(adir)):
        if name.startswith("releases-") and name.endswith(".jsonl.gz"):
            for _, _, line in sync_ocds.read_shard(os.path.join(adir, name)).values():
                rec = json.loads(line)
                by[sync_ocds.buyer_name(line).lower()].append(rec)
    return by


def days_between(a, b):
    try:
        t0 = time.strptime(a[:10], "%Y-%m-%d")
        t1 = time.strptime(b[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    return round((time.mktime(t1) - time.mktime(t0)) / 86400)


def rand(x):
    return "R{:,.0f}".format(x).replace(",", " ")


def top(counter, n=5):
    return ", ".join("%s (%d)" % (k or "unspecified", v) for k, v in counter.most_common(n))


def part_a(name, recs):
    """Markdown for the data half of the profile; deterministic for given data."""
    recs = sorted(recs, key=lambda r: sync_ocds.numeric_id(r.get("ocid", "")))
    dates = sorted((r.get("date") or "")[:10] for r in recs if r.get("date"))
    tenders = [r.get("tender") or {} for r in recs]
    cats = collections.Counter(t.get("mainProcurementCategory") or "" for t in tenders)
    methods = collections.Counter(t.get("procurementMethodDetails") or "" for t in tenders)
    windows = [d for d in (days_between((t.get("tenderPeriod") or {}).get("startDate"),
                                        (t.get("tenderPeriod") or {}).get("endDate"))
                           for t in tenders) if d is not None and d >= 0]
    docs = [len(t.get("documents") or []) for t in tenders]
    awards = [a for r in recs for a in (r.get("awards") or [])]
    values = [(a.get("value") or {}).get("amount") or 0 for a in awards]
    values = [v for v in values if v > 0]
    suppliers = collections.Counter(s.get("name") or "" for a in awards
                                    for s in (a.get("suppliers") or []))
    award_desc = collections.Counter(a.get("description") or "" for a in awards)
    contracts = sum(len(r.get("contracts") or []) for r in recs)
    emails = collections.Counter(
        ((p.get("contactPoint") or {}).get("email") or "").lower()
        for r in recs for p in (r.get("parties") or []))
    emails.pop("", None)

    lines = [
        PART_A_MARK,
        "## Part A: buyer data (from OCDS, updated by each sync)",
        "",
        "| | |",
        "| --- | --- |",
        "| Buyer | %s |" % name,
        "| Tenders in archive | %d |" % len(recs),
        "| First / latest release | %s / %s |" % (dates[0] if dates else "?",
                                                 dates[-1] if dates else "?"),
        "| Categories | %s |" % top(cats),
        "| Procurement methods | %s |" % top(methods),
        "| Bid window (days, median / min / max) | %s |" % (
            "%d / %d / %d" % (statistics.median(windows), min(windows), max(windows))
            if windows else "?"),
        "| Documents per tender (median) | %s |" % (
            "%g" % statistics.median(docs) if docs else "?"),
        "| Awards published | %d (contracts: %d) |" % (len(awards), contracts),
        "| Award value (median / max) | %s |" % (
            "%s / %s" % (rand(statistics.median(values)), rand(max(values)))
            if values else "none published"),
        "| Award notes (e.g. B-BBEE level) | %s |" % (top(award_desc) if awards else "-"),
        "| Top suppliers | %s |" % (top(suppliers) if suppliers else "-"),
        "| Contact emails | %s |" % (", ".join(e for e, _ in emails.most_common(3)) or "-"),
        "",
        "### Latest tenders",
        "",
    ]
    for r in recs[-10:][::-1]:
        t = r.get("tender") or {}
        lines.append("- [%s](%s) %s: %s" % (
            r.get("ocid"), RELEASE_URL % r.get("ocid"), (r.get("date") or "")[:10],
            " ".join(((t.get("description") or t.get("title") or "").split()))[:140]))
    lines += ["", COUNT_MARK % len(recs)]
    return "\n".join(lines)


def ensure_labels(repo):
    for label, (color, desc) in LABELS.items():
        gh("label", "create", label, "-R", repo, "--color", color,
           "--description", desc, "--force")


def existing_issues(repo):
    issues = gh_json("issue", "list", "-R", repo, "--label", "new-buyer", "--state", "all",
                     "--limit", "1000", "--json", "number,body,state") or []
    out = {}
    for i in issues:
        body = i.get("body") or ""
        start = body.find("<!-- ocds-buyer: ")
        if start >= 0:
            key = body[start + len("<!-- ocds-buyer: "):body.find(" -->", start)]
            out[key] = (i["number"], i["state"].upper())
    return out


def open_issue(repo, key, name, count):
    body = "\n".join([
        BUYER_MARK % key,
        "The OCDS Archive Sync found a buyer no earlier run had seen: **%s** "
        "(%d tenders)." % (name, count),
        "",
        "- **Part A** (data half, no AI) is the comment below; the sync keeps it current.",
        "- **Part B** (quirks from the tender packs) is pending; when it opens the "
        "corporate buyer-profile PR, label this `profile-pr-open` and link the PR.",
        "- Close this issue when the profile PR merges.",
    ])
    url = gh("issue", "create", "-R", repo, "--title", "New eTenders buyer: %s" % name,
             "--label", "new-buyer", "--label", "needs-quirks", "--body", body).strip()
    return int(url.rstrip("/").rsplit("/", 1)[1])


def upsert_part_a(repo, number, text):
    comments = gh_json("api", "repos/%s/issues/%d/comments" % (repo, number),
                       "--paginate") or []
    mine = next((c for c in comments if PART_A_MARK in (c.get("body") or "")), None)
    if mine is None:
        gh("issue", "comment", str(number), "-R", repo, "--body", text)
        return "posted"
    old = mine["body"]
    updates_at = old.find("\n### Updates")
    old_main = old if updates_at < 0 else old[:updates_at]
    updates = "" if updates_at < 0 else old[updates_at:]
    if old_main.strip() == text.strip():
        return "unchanged"
    prev = old_main.rsplit("<!-- ocds-part-a-tenders: ", 1)
    prev_n = int(prev[1].split(" ", 1)[0]) if len(prev) == 2 else None
    new_n = int(text.rsplit("<!-- ocds-part-a-tenders: ", 1)[1].split(" ", 1)[0])
    if prev_n is not None and prev_n != new_n:
        if not updates:
            updates = "\n### Updates\n"
        updates += "\n- %s: %+d tenders (now %d)" % (
            time.strftime("%Y-%m-%d", time.gmtime()), new_n - prev_n, new_n)
    gh("api", "--method", "PATCH", "repos/%s/issues/comments/%d" % (repo, mine["id"]),
       "--input", "-", input_text=json.dumps({"body": text + updates}))
    return "updated"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--archive-dir", required=True)
    ap.add_argument("--new-buyers", required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = ap.parse_args()
    if not args.repo:
        sys.exit("--repo or GITHUB_REPOSITORY is required")

    with open(args.new_buyers, encoding="utf-8") as f:
        new = json.load(f)
    by_buyer = records_by_buyer(args.archive_dir)
    ensure_labels(args.repo)
    issues = existing_issues(args.repo)

    for b in new:
        key = b["name"].lower()
        if key in issues:
            continue
        number = open_issue(args.repo, key, b["name"], b["tenders"])
        issues[key] = (number, "OPEN")
        print("opened #%d for %s" % (number, b["name"]))

    for key, (number, state) in sorted(issues.items(), key=lambda kv: kv[1][0]):
        if state != "OPEN" or key not in by_buyer:
            continue
        recs = by_buyer[key]
        name = sync_ocds.buyer_name(json.dumps(recs[0]))
        result = upsert_part_a(args.repo, number, part_a(name, recs))
        print("#%d %s: Part A %s" % (number, name, result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
