#!/usr/bin/env python3
"""Check the product files written with the product-strategy skill.

Usage:
  check_brief.py PATH [--product-name NAME] [--solution-words a,b,c]
  check_brief.py --self-test

PATH is the docs/product folder or a single Markdown file. All .md files in the folder are read
together, so the sections may live in one file or in several.

Checks (code, what fails):
  B01  a required section is missing (matched on the heading text, any level)
  B02  a required section is empty
  B03  Problem names the product or a solution word
  B04  Personas has no "Buyer:" line or no "User:" line
  B05  Jobs has no "Today:" line
  B06  Success metric lacks one of "Baseline:", "Target:", "By:", "Source:"
  B07  a row of the Alternatives table has neither an https URL plus a YYYY-MM-DD date nor "unverified"
  B08  an Assumptions item lacks "Risk:", "Test:", "Threshold:" or "By:", or names an unknown risk
  B09  Open decisions exists but is not a numbered list, or an item has no "Recommendation:"

Output: one finding per line as "path:line: code message". Exit 0 when clean, 1 with findings,
2 on a usage error. Python 3.8 or later, standard library only, no network.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

REQUIRED = [
    "problem", "personas", "jobs", "stress moment", "success metric", "non-goals",
    "alternatives", "table stakes",
    "competitive alternatives", "differentiated capabilities", "value", "best-fit customers",
    "market category", "assumptions",
]
SOLUTION_WORDS = [
    "app", "dashboard", "button", "screen", "feature", "platform", "integration", "api", "ai",
    "automation", "tool", "software", "portal", "plugin",
]
RISKS = {"value", "usability", "feasibility", "viability", "business viability"}
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def sections(files):
    """Return {title: (path, line, [body lines])}. A section runs to the next heading of the same or higher level."""
    out = {}
    for path, text in files:
        lines = text.splitlines()
        heads = []
        for i, line in enumerate(lines):
            m = HEADING.match(line)
            if m:
                heads.append((i, len(m.group(1)), m.group(2).strip().lower()))
        for k, (i, level, title) in enumerate(heads):
            end = len(lines)
            for j, lvl, _ in heads[k + 1:]:
                if lvl <= level:
                    end = j
                    break
            body = [ln for ln in lines[i + 1:end] if not HEADING.match(ln)]
            out.setdefault(title, (path, i + 1, body))
    return out


def has_text(body):
    return any(ln.strip() and not re.fullmatch(r"[\s\-|:]*", ln) for ln in body)


def check(files, product_name=None, solution_words=None):
    words = solution_words if solution_words is not None else SOLUTION_WORDS
    secs = sections(files)
    findings = []

    def add(path, line, code, msg):
        findings.append(f"{path}:{line}: {code} {msg}")

    first = files[0][0] if files else "-"
    for name in REQUIRED:
        if name not in secs:
            add(first, 0, "B01", f"missing section '{name}'")
        elif not has_text(secs[name][2]):
            add(secs[name][0], secs[name][1], "B02", f"section '{name}' is empty")

    def field_check(name, keys, code):
        if name in secs and has_text(secs[name][2]):
            path, line, body = secs[name]
            text = "\n".join(body)
            for key in keys:
                if not re.search(r"(?im)^\W*" + re.escape(key) + r"\s*:\s*\S", text):
                    add(path, line, code, f"'{name}' has no '{key}:' line with content")

    if "problem" in secs:
        path, line, body = secs["problem"]
        for off, ln in enumerate(body, start=1):
            low = ln.lower()
            if product_name and product_name.lower() in low:
                add(path, line + off, "B03", "Problem names the product")
            for w in words:
                if re.search(r"(?<![\w-])" + re.escape(w.lower()) + r"s?(?![\w-])", low):
                    add(path, line + off, "B03", f"Problem contains solution word '{w}'")
    field_check("personas", ["Buyer", "User"], "B04")
    field_check("jobs", ["Today"], "B05")
    field_check("success metric", ["Baseline", "Target", "By", "Source"], "B06")

    if "alternatives" in secs:
        path, line, body = secs["alternatives"]
        rows = [(off, ln) for off, ln in enumerate(body, start=1) if ln.strip().startswith("|")]
        for off, ln in rows[2:]:  # skip header and separator
            ok = re.search(r"https://\S+", ln) and re.search(r"\b\d{4}-\d{2}-\d{2}\b", ln)
            if not ok and "unverified" not in ln.lower():
                add(path, line + off, "B07", "alternative without https source and read date, and not marked unverified")

    if "assumptions" in secs:
        path, line, body = secs["assumptions"]
        items, cur = [], None
        for off, ln in enumerate(body, start=1):
            if re.match(r"^(\d+\.|-)\s+", ln):
                cur = [off, ln]
                items.append(cur)
            elif cur is not None and ln.strip():
                cur[1] += "\n" + ln
        for off, text in items:
            for key in ("Risk", "Test", "Threshold", "By"):
                if not re.search(r"(?i)\b" + key + r"\s*:\s*\S", text):
                    add(path, line + off, "B08", f"assumption has no '{key}:'")
            m = re.search(r"(?i)\bRisk\s*:\s*([a-z ]+?)(?:[.;,\n]|$)", text)
            if m and m.group(1).strip().lower() not in RISKS:
                add(path, line + off, "B08", f"unknown risk '{m.group(1).strip()}' (value, usability, feasibility, viability)")

    if "open decisions" in secs and has_text(secs["open decisions"][2]):
        path, line, body = secs["open decisions"]
        numbered = [(off, ln) for off, ln in enumerate(body, start=1) if re.match(r"^\d+\.\s", ln)]
        if not numbered:
            add(path, line, "B09", "Open decisions is not a numbered list")
        text = "\n".join(body)
        parts = re.split(r"(?m)^\d+\.\s", text)[1:]
        for (off, _), part in zip(numbered, parts):
            if "recommendation:" not in part.lower():
                add(path, line + off, "B09", "decision without 'Recommendation:'")
    return findings


def load(path):
    if os.path.isdir(path):
        names = sorted(n for n in os.listdir(path) if n.endswith(".md"))
        return [(os.path.join(path, n), open(os.path.join(path, n), encoding="utf-8").read()) for n in names]
    return [(path, open(path, encoding="utf-8").read())]


GOOD = """# Product brief
## Problem
Site leads at small architecture offices learn about a changed client deadline from a forwarded mail and
rebuild the week's work plan by hand; a missed change costs a weekend.
## Personas
Buyer: office owner, judges cost and client complaints.
User: project lead, judges how fast the plan is current.
## Jobs
Project lead: keep five people on the right drawings when the client moves a date.
Today: shared spreadsheet plus a group chat.
## Stress moment
The day before a client deadline, five people editing at once.
## Success metric
Metric: plans corrected within one hour of a date change.
Baseline: not measured yet.
Target: 80 percent.
By: 2027-06-30
Source: query over plan change events.
## Non-goals
No time tracking. No invoicing.
## Alternatives
| Alternative | Claim | Source | Read |
|---|---|---|---|
| Spreadsheet and chat | free, no deadline view | interview notes 2026-09-12 | 2026-09-12 https://example.com/notes |
| Vendor A | per-seat price | unverified | |
## Table stakes
Shared calendar, comments, mobile view.
## Competitive alternatives
Spreadsheet and chat.
## Differentiated capabilities
Date changes propagate to every affected drawing.
## Value
Nobody works on an outdated plan.
## Best-fit customers
Offices with 3 to 15 people and fixed client deadlines.
## Market category
Project planning for architecture offices.
## Assumptions
1. Project leads update dates themselves. Risk: value. Test: five interviews. Threshold: 4 of 5. By: 2026-12-01
## Open decisions
1. First segment: architecture only or all planning offices?
   Recommendation: architecture only, because the interviews cover it.
"""

BAD = """## Problem
They need a dashboard app for deadlines in PlanBoard.
## Personas
User: project lead.
## Jobs
Keep plans current.
## Success metric
Target: more users.
## Alternatives
| Alternative | Claim | Source |
|---|---|---|
| Vendor B | has SSO on all plans | heard at a fair |
## Assumptions
- People want it. Risk: hope.
## Open decisions
- pick a segment
"""


def self_test():
    ok = True
    good = check([("good.md", GOOD)], product_name="PlanBoard")
    if good:
        print("self-test: good fixture produced findings:\n" + "\n".join(good))
        ok = False
    bad = check([("bad.md", BAD)], product_name="PlanBoard")
    codes = {f.split(": ", 1)[1].split(" ", 1)[0] for f in bad}
    for code in ["B01", "B03", "B04", "B05", "B06", "B07", "B08", "B09"]:
        if code not in codes:
            print(f"self-test: bad fixture did not trigger {code}")
            ok = False
    empty = check([("empty.md", GOOD.replace("No time tracking. No invoicing.", ""))])
    if not any(" B02 " in f for f in empty):
        print("self-test: empty Non-goals did not trigger B02")
        ok = False
    with tempfile.TemporaryDirectory() as d:
        half = GOOD.index("## Alternatives")
        for name, text in (("brief.md", GOOD[:half]), ("market.md", GOOD[half:])):
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                fh.write(text)
        split = check(load(d))
        if split:
            print("self-test: folder layout produced findings:\n" + "\n".join(split))
            ok = False
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?")
    ap.add_argument("--product-name")
    ap.add_argument("--solution-words", help="comma-separated words that mark a solution in the Problem section")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.path or not os.path.exists(args.path):
        ap.print_usage(sys.stderr)
        return 2
    words = [w.strip() for w in args.solution_words.split(",") if w.strip()] if args.solution_words else None
    findings = check(load(args.path), args.product_name, words)
    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
