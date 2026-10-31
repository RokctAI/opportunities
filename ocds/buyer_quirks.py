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
"""Part B for new-buyer issues: read the buyer's tender packs and post quirks.

For each open issue labelled needs-quirks that has no Part B comment yet:
  1. pick the buyer's latest tenders that carry documents (from the archive)
  2. download the PDFs (eTenders document URLs need no auth)
  3. extract text with pdftotext, OCR with tesseract when a PDF is scanned
  4. scan the text with fixed rules (briefing, CIDB, functionality pass mark,
     preference system, forms, local content, submission method, ...)
  5. build a prompt from Part A + the scan + the pack text (saved to --out-dir)
  6. call an AI if one is configured: text in, JSON out, no repo access.
     QUIRKS_AI_CMD runs any provider as a shell command (JSON request on
     stdin, JSON reply on stdout); else GROQ_API_KEY (QUIRKS_MODEL picks the
     model); else ANTHROPIC_API_KEY.
     With neither, the comment carries a checklist for a person to finish.
  7. post the result as one Part B comment on the issue
Opening the buyer-profile PR (and the profile-pr-open label) is not done here.

Usage (gh authenticated; GITHUB_REPOSITORY set):
  python ocds/buyer_quirks.py --archive-dir ocds-data [--max-issues 3] [--packs 3]
  python ocds/buyer_quirks.py --archive-dir ocds-data --buyer "Name" --dry-run
"""

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import buyer_issues  # noqa: E402

PART_B_MARK = "<!-- ocds-part-b -->"
MODEL = "claude-opus-5-5"
MAX_PDF_BYTES = 40 * 1024 * 1024
MAX_PROMPT_CHARS = 1_200_000  # ~300k tokens; well inside the 1M context
SCANNED_CHARS_PER_PAGE = 200
OCR_MAX_PAGES = 40
UA = "RokctAI-opportunities-ocds-sync (+https://github.com/RokctAI/opportunities)"

I = re.IGNORECASE
FORM_FAMILIES = r"SBD|MBD|PBD|WCBD|WCPP|ECBD|GPBD|KZNBD|LPBD|MPBD|NCBD|NWBD|FSBD"
BODIES = ["SAICA", "SAIPA", "IRBA", "IIA", "ECSA", "SACPCMP", "SACAP", "SACQSP", "PSIRA",
          "NHBRC", "SACNASP", "LPC", "ICASA", "SABS", "SANAS", "SAHPRA", "SAQA", "SETA",
          "CIPC", "PSiRA", "FSCA", "SAPS clearance"]


def _snip(text, m, width=90):
    a, b = max(0, m.start() - width), min(len(text), m.end() + width)
    return " ".join(text[a:b].split())


def _first(text, patterns, value):
    for p in patterns:
        m = re.search(p, text, I)
        if m:
            return [(value(m), _snip(text, m))]
    return []


def _all(text, pattern, value, limit=6):
    out, seen = [], set()
    for m in re.finditer(pattern, text, I):
        v = value(m)
        if v and v not in seen:
            seen.add(v)
            out.append((v, _snip(text, m)))
            if len(out) >= limit:
                break
    return out


def scan(text):
    """Fixed-rule scan of one pack. Returns {rule: [(value, evidence), ...]}."""
    t = text
    found = {
        "Briefing / site meeting": _all(
            t, r"\b(compulsory|mandatory|non[- ]compulsory|optional)\s+(?:virtual\s+|online\s+)?"
               r"(?:pre[- ]?bid\s+|pre[- ]?tender\s+|tender\s+|bid\s+|clarification\s+|site\s+)?"
               r"(briefing(?:\s+session)?|site\s+(?:visit|inspection|meeting)|clarification\s+meeting)",
            lambda m: "%s %s" % (m.group(1).lower(), " ".join(m.group(2).lower().split())), 3),
        "CIDB grading": _all(
            t, r"\bCIDB\b[^\n]{0,120}?\b([1-9])\s?(CE|GB|EB|ME|EP|SB|SC|SD|SE|SF|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SQ)\b",
            lambda m: m.group(1) + m.group(2).upper(), 4),
        "Functionality pass mark": _first(t, [
            r"functionality[^\n.]{0,160}?(?:minimum|threshold|at least|score of|qualifying score)"
            r"\D{0,30}?(\d{2})\s*(%|points|percent)",
            r"(?:minimum|threshold|at least)\D{0,30}?(\d{2})\s*(%|points|percent)[^\n.]{0,80}?functionality",
            r"(?:minimum\s+)?qualifying\s+(?:threshold|score)\D{0,10}(\d{2})\s*(%|out\s+of\s+100|points)",
        ], lambda m: "%s %s" % (m.group(1), "%" if m.group(2) in ("%",) or m.group(2).lower() == "percent"
                                else "points")),
        "Preference point system": _first(t, [
            r"(80/20|90/10)[^\n.]{0,60}?(?:will|shall)\s+be\s+(?:utili[sz]ed|applied|used)",
            r"(?:will|shall)\s+be\s+(?:utili[sz]ed|applied|used|evaluated)[^\n.]{0,60}?(80/20|90/10)",
            r"(80/20|90/10)\s+preference\s+point\s+system\s+(?:applies|is applicable)",
        ], lambda m: m.group(1)),
        "Bid forms": [],
        "Local content": _all(
            t, r"local\s+(?:content|production)[^\n.]{0,100}?(\d{2,3})\s*%",
            lambda m: m.group(1) + "%", 3),
        "CSD registration": _first(t, [r"central\s+supplier\s+database|\bCSD\b|\bMAAA\d"],
                                   lambda m: "required/mentioned"),
        "Tax compliance": _first(t, [r"tax\s+compliance\s+status|\bTCS\b|SARS\s+(?:e-?filing\s+)?pin"],
                                 lambda m: "TCS / SARS PIN"),
        "Submission method": [],
        "Bid validity": _first(t, [
            r"valid(?:ity)?(?:\s+period)?[^\n]{0,50}?(\d{2,3})\s*(?:calendar\s+|working\s+|business\s+)?days"],
            lambda m: m.group(1) + " days"),
        "Guarantees / retention": _all(
            t, r"(bid\s+bond|tender\s+guarantee|performance\s+(?:guarantee|security)|retention)"
               r"[^\n.]{0,80}?(\d{1,2}(?:[.,]\d+)?)\s*%",
            lambda m: "%s %s%%" % (" ".join(m.group(1).lower().split()), m.group(2)), 3),
        # The PPPFA clause "may not subcontract more than 25% ... to a non-HDI" is
        # standard; only a required minimum is a quirk.
        "Required subcontracting": _first(t, [
            r"(?:must|shall|required\s+to|minimum\s+of|at\s+least)\s+sub-?contract[^\n.]{0,80}?(\d{1,2})\s*%",
            r"(?:minimum\s+of|at\s+least)\s+(\d{1,2})\s*%[^\n.]{0,80}?sub-?contract",
        ], lambda m: "at least " + m.group(1) + "%"),
        "Professional registrations": [],
        "Document fee": _first(t, [
            r"non-?refundable\s+(?:fee|amount|deposit|tender\s+fee|document\s+fee)[^\n]{0,60}?R\s?(\d[\d ,.]*\d)"],
            lambda m: "R" + m.group(1).replace(" ", "")),
        "Specific goals": [],
        "Joint ventures / consortia": _first(t, [r"joint\s+venture|consorti(?:um|a)"],
                                             lambda m: "provisions present"),
    }

    forms = collections.defaultdict(set)
    for m in re.finditer(r"\b(%s)\s?(\d{1,2}(?:\.\d)?)\b" % FORM_FAMILIES, t):
        forms[m.group(1).upper()].add(m.group(2))
    found["Bid forms"] = [
        ("%s %s" % (fam, ", ".join(sorted(nums, key=lambda x: float(x)))), "")
        for fam, nums in sorted(forms.items())]

    sub = []
    for label, p in [("tender box", r"tender\s+box|bid\s+box"),
                     ("sealed envelope", r"sealed\s+envelope"),
                     ("two-envelope", r"two[- ]envelope|separate\s+(?:sealed\s+)?envelopes?"),
                     ("email", r"e-?mail(?:ed)?\s+(?:submissions?|bids?|to)\b|submitted\s+(?:via|by)\s+e-?mail"),
                     ("eTenders portal", r"e-?tender(?:s)?\s+portal|electronic(?:ally)?\s+submi"),
                     ("hard copies", r"hard\s+cop(?:y|ies)|original\s+and\s+(?:one|two|\d)\s+cop"),
                     ("USB / flash drive", r"\bUSB\b|flash\s+drive|memory\s+stick"),
                     ("courier / hand delivery", r"courier|hand[- ]deliver")]:
        sub += _first(t, [p], lambda m, label=label: label)
    found["Submission method"] = sub

    regs = []
    for b in BODIES:
        m = re.search(r"\b%s\b" % re.escape(b), t)
        if m:
            regs.append((b, _snip(t, m)))
    found["Professional registrations"] = regs

    goals = []
    for m in re.finditer(r"specific\s+goals?", t, I):
        window = t[m.start():m.start() + 1500].lower()
        for label, p in [("black ownership", r"black"), ("women", r"wom[ae]n"), ("youth", r"youth"),
                         ("disability", r"disab"), ("military veterans", r"veteran"),
                         ("local / township / rural", r"township|rural|local\s+(?:enterprise|supplier|municipal)"),
                         ("EME / QSE", r"\bEME\b|\bQSE\b"), ("HDI", r"\bHDI\b|historically\s+disadvantaged")]:
            if re.search(p, window) and label not in [g[0] for g in goals]:
                goals.append((label, ""))
        if goals:
            break
    found["Specific goals"] = goals
    return {k: v for k, v in found.items() if v}


def pick_packs(recs, n):
    with_docs = [r for r in recs if any(
        (d.get("url") or "") for d in ((r.get("tender") or {}).get("documents") or []))]
    with_docs.sort(key=lambda r: (r.get("date") or "", buyer_issues.sync_ocds.numeric_id(r["ocid"])))
    return with_docs[-n:][::-1]


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:  # nosec B310
        size = 0
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_PDF_BYTES:
                raise ValueError("larger than %d MB" % (MAX_PDF_BYTES >> 20))
            f.write(chunk)
    with open(dest, "rb") as f:
        if f.read(5) != b"%PDF-":
            raise ValueError("not a PDF")


def pdf_pages(path):
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=60, check=False).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
        return int(m.group(1)) if m else 0
    except (OSError, subprocess.SubprocessError):
        return 0


def pdf_text(path, workdir):
    """Returns (text, pages, method)."""
    pages = pdf_pages(path)
    txt = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True,
                         text=True, timeout=300, check=False).stdout
    if len(txt.strip()) >= SCANNED_CHARS_PER_PAGE * max(pages, 1) or not (
            shutil.which("tesseract") and shutil.which("pdftoppm")):
        method = "text" if len(txt.strip()) >= SCANNED_CHARS_PER_PAGE * max(pages, 1) else "scanned (no OCR)"
        return txt, pages, method
    prefix = os.path.join(workdir, "page")
    last = min(pages or OCR_MAX_PAGES, OCR_MAX_PAGES)
    subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", "-l", str(last), path, prefix],
                   check=True, timeout=1200)
    parts = []
    for img in sorted(f for f in os.listdir(workdir) if f.startswith("page") and f.endswith(".png")):
        parts.append(subprocess.run(["tesseract", os.path.join(workdir, img), "-", "--psm", "1"],
                                    capture_output=True, text=True, timeout=300,
                                    check=False).stdout)
        os.remove(os.path.join(workdir, img))
    method = "OCR" + (" (first %d of %d pages)" % (last, pages) if pages > last else "")
    return "\n".join(parts), pages, method


def read_packs(recs, n, workdir):
    packs = []
    for r in pick_packs(recs, n):
        t = r.get("tender") or {}
        for i, d in enumerate(t.get("documents") or []):
            url = d.get("url") or ""
            if not url:
                continue
            entry = {"ocid": r["ocid"], "tender": t.get("title") or "", "date": (r.get("date") or "")[:10],
                     "document": d.get("title") or "", "url": url}
            pdf = os.path.join(workdir, "%s-%d.pdf" % (r["ocid"], i))
            try:
                download(url, pdf)
                ocr_dir = tempfile.mkdtemp(dir=workdir)
                entry["text"], entry["pages"], entry["method"] = pdf_text(pdf, ocr_dir)
                entry["scan"] = scan(entry["text"])
            except Exception as e:  # one bad document must not stop the buyer
                entry.update(text="", pages=0, method="failed: %s" % e, scan={})
            packs.append(entry)
    return packs


QUIRKS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "quirks": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "detail": {"type": "string"},
                "evidence": {"type": "string"},
                "ocids": {"type": "array", "items": {"type": "string"}},
                "severity": {"type": "string", "enum": ["disqualifying", "important", "minor"]},
            },
            "required": ["title", "detail", "evidence", "ocids", "severity"],
            "additionalProperties": False,
        }},
        "scan_corrections": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "quirks", "scan_corrections"],
    "additionalProperties": False,
}

SYSTEM = (
    "You review South African public-sector tender packs for one buyer, to build that "
    "buyer's profile for bidders. A quirk is anything in this buyer's packs that differs "
    "from the standard National Treasury bid pack (SBD forms, PPPFA 2022 preference "
    "points, CSD and tax compliance) or that is likely to get a bidder disqualified: "
    "unusual returnables, own forms instead of SBD, compulsory meetings, odd submission "
    "rules, pass marks, registrations, guarantees, subcontracting, pricing format, and "
    "similar. Report only what the pack text supports, quote the evidence, and name the "
    "ocids it comes from. Say when a pattern repeats across packs, since that is what "
    "makes it a buyer quirk rather than a one-off. Use scan_corrections for any line of "
    "the automatic scan that the text shows is wrong.")


KEY_WORDS = re.compile(
    r"returnable|mandatory|compulsory|disqualif|eliminat|evaluation|functionality|criteria|"
    r"special\s+conditions|must\s+(?:submit|be|attach|provide)|failure\s+to|will\s+not\s+be\s+considered|"
    r"briefing|submission|pricing\s+schedule|scope\s+of\s+work|terms\s+of\s+reference", I)
BOILERPLATE = re.compile(
    r"GENERAL\s+CONDITIONS\s+OF\s+CONTRACT|PREFERENCE\s+POINTS\s+CLAIM\s+FORM|"
    r"DECLARATION\s+OF\s+INTEREST|BIDDER.S\s+DISCLOSURE", I)


def condense(text, budget):
    """Keep the pages most likely to hold quirks, in page order, within budget chars."""
    if len(text) <= budget:
        return text
    pages = text.split("\f")
    scored = sorted(range(len(pages)), key=lambda i: -(
        len(KEY_WORDS.findall(pages[i])) - (8 if BOILERPLATE.search(pages[i]) else 0)))
    keep, used = set(), 0
    for i in scored:
        if used + len(pages[i]) > budget:
            continue
        keep.add(i)
        used += len(pages[i])
    dropped = len(pages) - len(keep)
    return "\f".join(pages[i] for i in sorted(keep)) + (
        "\n[%d of %d pages left out to fit the AI's input limit; standard forms first]"
        % (dropped, len(pages)))


def build_prompt(name, part_a_md, packs, max_chars=MAX_PROMPT_CHARS):
    per_pack = max_chars // max(len(packs), 1)
    blocks, used = [], 0
    for p in packs:
        head = "=== %s | %s | %s | %s (%s pages, %s) ===" % (
            p["ocid"], p["date"], p["tender"], p["document"], p["pages"], p["method"])
        body = condense(p["text"], per_pack)
        room = max_chars - used - len(head)
        if room <= 0:
            blocks.append(head + "\n[left out: prompt size limit reached]")
            continue
        if len(body) > room:
            body = body[:room] + "\n[cut here: prompt size limit reached]"
        used += len(head) + len(body)
        blocks.append(head + "\n" + body)
    scan_json = json.dumps([{"ocid": p["ocid"], "document": p["document"], "scan": p["scan"]}
                            for p in packs], indent=1, ensure_ascii=False)
    return ("Buyer: %s\n\n## Part A (archive data)\n%s\n\n## Automatic scan\n%s\n\n"
            "## Tender pack text\n%s" % (name, part_a_md, scan_json, "\n\n".join(blocks)))


def _valid(data):
    if not isinstance(data, dict) or not isinstance(data.get("quirks"), list):
        return False
    need = QUIRKS_SCHEMA["properties"]["quirks"]["items"]["required"]
    return all(isinstance(q, dict) and all(k in q for k in need) for q in data["quirks"])


def call_command(cmd, prompt):
    """Any AI behind a shell command: JSON {system, prompt, schema} on stdin, JSON out."""
    req = json.dumps({"system": SYSTEM, "prompt": prompt, "schema": QUIRKS_SCHEMA})
    for _ in (1, 2):
        try:
            out = subprocess.run(cmd, shell=True, input=req, capture_output=True,  # nosec B602
                                 text=True, timeout=1800, check=False)
            data = json.loads(out.stdout)
            if out.returncode == 0 and _valid(data):
                return data, "AI step: QUIRKS_AI_CMD."
        except (ValueError, subprocess.SubprocessError, OSError):
            pass
    return None, "AI step (QUIRKS_AI_CMD) returned unusable JSON twice."


def call_anthropic(prompt):
    import anthropic
    client = anthropic.Anthropic()
    for attempt in (1, 2):
        try:
            with client.beta.messages.stream(
                model=os.environ.get("QUIRKS_MODEL", MODEL),
                max_tokens=32000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={"effort": "high",
                               "format": {"type": "json_schema", "schema": QUIRKS_SCHEMA}},
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                msg = stream.get_final_message()
        except anthropic.APIStatusError as e:
            if attempt == 2:
                return None, "AI step failed: HTTP %s." % e.status_code
            continue
        except anthropic.APIConnectionError:
            if attempt == 2:
                return None, "AI step failed: connection error."
            continue
        if msg.stop_reason == "refusal":
            return None, "AI step declined the request."
        try:
            data = json.loads(next((b.text for b in msg.content if b.type == "text"), ""))
            if _valid(data):
                return data, "AI step: %s." % msg.model
        except ValueError:
            pass
    return None, "AI step returned unusable JSON twice."


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"


def call_groq(prompt):
    """Groq's OpenAI-compatible chat API with a JSON-schema reply (stdlib only)."""
    model = os.environ.get("QUIRKS_MODEL", GROQ_MODEL)
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "quirks", "schema": QUIRKS_SCHEMA}},
    }).encode()
    last = "unusable JSON"
    for _ in (1, 2):
        req = urllib.request.Request(GROQ_URL, data=body, headers={
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"],
            "Content-Type": "application/json", "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:  # nosec B310
                reply = json.load(resp)
            data = json.loads(reply["choices"][0]["message"]["content"])
            if _valid(data):
                return data, "AI step: Groq %s." % model
        except urllib.error.HTTPError as e:
            last = "HTTP %s: %s" % (e.code, e.read()[:200].decode("utf-8", "replace"))
        except (urllib.error.URLError, ValueError, KeyError, IndexError) as e:
            last = str(e)[:200]
    return None, "AI step (Groq %s) failed twice: %s" % (model, " ".join(last.split()))


def ai_provider():
    if os.environ.get("QUIRKS_AI_CMD"):
        return "command"
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def call_model(prompt):
    """Prompt in, JSON out; the AI never touches the repo. Returns (dict or None, note).

    First match wins: QUIRKS_AI_CMD (any provider, see call_command),
    GROQ_API_KEY, ANTHROPIC_API_KEY. With none, Part B is left for a person.
    """
    provider = ai_provider()
    if provider == "command":
        return call_command(os.environ["QUIRKS_AI_CMD"], prompt)
    if provider == "groq":
        return call_groq(prompt)
    if provider == "anthropic":
        return call_anthropic(prompt)
    return None, "No AI configured, so this is for a person to finish."


HUMAN_STEPS = [
    "### For a person to finish",
    "",
    "- [ ] Open the documents below and check each line of the automatic scan; "
    "correct any that are wrong.",
    "- [ ] Add each quirk as a line under **Quirks**: `**title** (disqualifying / "
    "important / minor): what it means for a bidder. > quote from the pack. ocids`",
    "- [ ] Note which quirks repeat across tenders; those are the buyer's habits.",
    "",
    "The prompt the AI would get is saved in this run's `buyer-quirks` artifact, "
    "so it can also be pasted into any AI chat by hand.",
    "",
    "**Quirks**",
    "",
    "- ",
    "",
]


def summarise_scan(packs):
    per_rule = collections.defaultdict(collections.Counter)
    for p in packs:
        for rule, hits in p["scan"].items():
            for value in {v for v, _ in hits}:
                per_rule[rule][value] += 1
    return per_rule


def render(name, packs, ai, ai_note):
    read = [p for p in packs if p["text"].strip()]
    n_tenders = len({p["ocid"] for p in read})
    lines = [PART_B_MARK, "## Part B: pack quirks", "",
             "Read %d document(s) from %d tender(s)." % (len(read), n_tenders), ""]
    if ai:
        lines += ["### Quirks", "", ai.get("summary", ""), ""]
        order = {"disqualifying": 0, "important": 1, "minor": 2}
        for q in sorted(ai["quirks"], key=lambda q: order.get(q.get("severity"), 3)):
            lines.append("- **%s** (%s): %s  \n  > %s  \n  _%s_" % (
                q["title"], q["severity"], q["detail"], " ".join(q["evidence"].split())[:400],
                ", ".join(q["ocids"])))
        if ai.get("scan_corrections"):
            lines += ["", "Scan corrections:"] + ["- " + c for c in ai["scan_corrections"]]
        lines.append("")
    lines += ["_%s_" % ai_note, ""]
    if not ai:
        lines += HUMAN_STEPS
    lines += ["### Automatic scan (no AI)", "",
              "| Check | Found | Packs |", "| --- | --- | --- |"]
    per_rule = summarise_scan(read)
    for rule, counts in per_rule.items():
        lines.append("| %s | %s | %s |" % (rule, "; ".join(v for v, _ in counts.most_common()),
                                           ", ".join("%d/%d" % (c, len(read)) for _, c in counts.most_common())))
    missing = [r for r in ("Briefing / site meeting", "Functionality pass mark",
                           "Preference point system", "Bid validity") if r not in per_rule]
    if missing:
        lines += ["", "Not found by the scan: %s." % ", ".join(missing)]
    lines += ["", "### Documents read", ""]
    for p in packs:
        lines.append("- [%s](%s) %s, %s: %s (%s pages, %s)" % (
            p["ocid"], p["url"], p["date"], p["tender"][:80], p["document"][:80], p["pages"], p["method"]))
    lines += ["", "Next: check this, open the buyer-profile PR, then label this issue "
              "`profile-pr-open` and link the PR."]
    return "\n".join(lines)


def upsert_part_b(repo, number, text):
    comments = buyer_issues.gh_json("api", "repos/%s/issues/%d/comments" % (repo, number),
                                    "--paginate") or []
    mine = next((c for c in comments if PART_B_MARK in (c.get("body") or "")), None)
    if mine is None:
        buyer_issues.gh("issue", "comment", str(number), "-R", repo, "--body", text)
        return "posted"
    buyer_issues.gh("api", "--method", "PATCH", "repos/%s/issues/comments/%d" % (repo, mine["id"]),
                    "--input", "-", input_text=json.dumps({"body": text}))
    return "updated"


def has_part_b(repo, number):
    comments = buyer_issues.gh_json("api", "repos/%s/issues/%d/comments" % (repo, number),
                                    "--paginate") or []
    return any(PART_B_MARK in (c.get("body") or "") for c in comments)


def process(name, recs, args, workdir):
    packs = read_packs(recs, args.packs, workdir)
    part_a_md = buyer_issues.part_a(name, recs)
    # Groq models have ~128k-token windows and tight per-minute token limits.
    budget = int(os.environ.get("QUIRKS_MAX_CHARS") or (
        120_000 if ai_provider() == "groq" else MAX_PROMPT_CHARS))
    prompt = build_prompt(name, part_a_md, packs, budget)
    slug = os.path.join(args.out_dir, re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"))
    with open(slug + ".prompt.md", "w", encoding="utf-8") as f:
        f.write("# System\n\n%s\n\n# Reply format (JSON schema)\n\n```json\n%s\n```\n\n# Input\n\n%s\n"
                % (SYSTEM, json.dumps(QUIRKS_SCHEMA, indent=1), prompt))
    ai, note = (None, "AI step skipped (--no-ai), so this is for a person to finish.") \
        if args.no_ai else call_model(prompt)
    with open(slug + ".json", "w", encoding="utf-8") as f:
        json.dump({"buyer": name, "ai": ai, "ai_note": note,
                   "packs": [{k: v for k, v in p.items() if k != "text"} for p in packs]},
                  f, indent=1, ensure_ascii=False)
    return render(name, packs, ai, note)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--archive-dir", required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--max-issues", type=int, default=3, help="issues to process per run")
    ap.add_argument("--packs", type=int, default=3, help="latest tenders to read per buyer")
    ap.add_argument("--buyer", help="process one buyer by name and print the comment (no issue)")
    ap.add_argument("--refresh", action="store_true", help="redo issues that already have Part B")
    ap.add_argument("--no-ai", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print comments instead of posting")
    ap.add_argument("--out-dir", default="buyer-quirks")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    by_buyer = buyer_issues.records_by_buyer(args.archive_dir)

    with tempfile.TemporaryDirectory() as workdir:
        if args.buyer:
            recs = by_buyer.get(" ".join(args.buyer.split()).lower())
            if not recs:
                sys.exit("buyer not found: %s" % args.buyer)
            print(process(args.buyer, recs, args, workdir))
            return 0
        if not args.repo:
            sys.exit("--repo or GITHUB_REPOSITORY is required")
        issues = buyer_issues.existing_issues(args.repo)
        labelled = buyer_issues.gh_json(
            "issue", "list", "-R", args.repo, "--label", "needs-quirks", "--state", "open",
            "--limit", "1000", "--json", "number") or []
        wanted = {i["number"] for i in labelled}
        done = 0
        for key, (number, state) in sorted(issues.items(), key=lambda kv: kv[1][0]):
            if done >= args.max_issues:
                break
            if state != "OPEN" or number not in wanted or key not in by_buyer:
                continue
            if not args.refresh and has_part_b(args.repo, number):
                continue
            recs = by_buyer[key]
            name = buyer_issues.sync_ocds.buyer_name(json.dumps(recs[0]))
            text = process(name, recs, args, workdir)
            if args.dry_run:
                print("--- #%d %s\n%s" % (number, name, text))
            else:
                print("#%d %s: Part B %s" % (number, name, upsert_part_b(args.repo, number, text)))
            done += 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
