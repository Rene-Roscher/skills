#!/usr/bin/env python3
"""Check a stored market analysis before it is used for a decision.

Usage:
  check_market_analysis.py docs/business/market-analysis-2026-11.md [--today YYYY-MM-DD]
  check_market_analysis.py --self-test

Findings print as `path:line: error|warning ID message`. Exit 1 on any error.

Checks:
  M01 file name is market-analysis-YYYY-MM.md and matches the prepared month
  M02 prepared and valid_until exist, and valid_until is 3 to 6 months after prepared
  M03 the analysis has expired (today is after valid_until): refresh before use
  M04 10 to 30 companies, each with a known kind
  M05 every fact row has an https source, an access date not in the future, and a label
  M06 an inferred fact names the facts it was inferred from ("from F012")
  M07 every company has at least one pricing fact (it may say "not public")
  M08 every synthesis section exists and is not empty
  M09 every recommendation cites existing fact IDs after "Evidence:"
  M10 a fact names a company that is not in the companies table
  M11 a pricing fact without a currency and a billing period
  M12 warning: a pricing fact that does not say net or gross
  M13 warning: a fact read more than 45 days before the prepared date
  M14 warning: no company of kind incumbent or workaround, or none of kind top-tier
  M15 warning: a recommendation that rests only on inferred facts
Python standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

KINDS = {"direct", "adjacent", "incumbent", "workaround", "top-tier", "new-entrant"}
LABELS = {"verified", "reported", "inferred"}
FIELDS = {
    "positioning", "target", "pricing", "value-metric", "limits", "free-tier", "annual-discount",
    "features", "gaps", "channels", "reviews", "changelog", "team", "funding", "other",
}
SECTIONS = ["Price corridor", "Table stakes", "White spaces", "Threats", "Recommendations", "Open questions"]
CURRENCY_RE = re.compile(r"\b(EUR|USD|GBP|CHF|SEK|NOK|DKK|PLN|CAD|AUD|JPY)\b|[€$£]")
PERIOD_RE = re.compile(r"\b(month|monthly|year|yearly|annual|annually|one-time|once|per day|per week)\b", re.I)
NETGROSS_RE = re.compile(r"\b(net|gross|excl\.?|incl\.?|excluding|including|plus VAT|VAT)\b", re.I)
NOT_PUBLIC_RE = re.compile(r"\bnot public\b", re.I)
FACT_ID_RE = re.compile(r"\bF\d{3}\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def add_months(d: dt.date, months: int) -> dt.date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):
        try:
            return dt.date(year, month, day)
        except ValueError:
            continue
    raise ValueError("unreachable")


def parse_date(s: str) -> dt.date | None:
    s = s.strip()
    if not DATE_RE.match(s):
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def table_rows(lines: list[str], start: int) -> list[tuple[int, list[str]]]:
    """Rows of the first Markdown table after line index `start`, without header and separator."""
    rows, seen_sep = [], False
    i = start
    while i < len(lines) and not lines[i].lstrip().startswith("|"):
        if lines[i].startswith("## "):
            return rows
        i += 1
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            seen_sep = True
        elif seen_sep:
            rows.append((i + 1, cells))
        i += 1
    return rows


def check(path: str, text: str, today: dt.date) -> list[tuple[int, str, str, str]]:
    out: list[tuple[int, str, str, str]] = []
    err = lambda n, c, m: out.append((n, "error", c, m))  # noqa: E731
    warn = lambda n, c, m: out.append((n, "warning", c, m))  # noqa: E731
    lines = text.splitlines()

    heads = {}
    for i, line in enumerate(lines):
        m = re.match(r"^(prepared|valid_until):\s*(\S+)\s*$", line)
        if m and m.group(1) not in heads:
            heads[m.group(1)] = (i + 1, parse_date(m.group(2)))
    prepared = heads.get("prepared", (1, None))[1]
    valid_until = heads.get("valid_until", (1, None))[1]
    if prepared is None or valid_until is None:
        err(1, "M02", "header needs 'prepared: YYYY-MM-DD' and 'valid_until: YYYY-MM-DD'")
    else:
        n = heads["valid_until"][0]
        if not add_months(prepared, 3) <= valid_until <= add_months(prepared, 6):
            err(n, "M02", f"valid_until {valid_until} is not 3 to 6 months after prepared {prepared}")
        if today > valid_until:
            err(n, "M03", f"expired on {valid_until}; refresh the analysis before using it for a decision")

    m = re.search(r"market-analysis-(\d{4})-(\d{2})\.md$", path)
    if not m:
        err(1, "M01", "file name must be market-analysis-YYYY-MM.md")
    elif prepared and (int(m.group(1)), int(m.group(2))) != (prepared.year, prepared.month):
        err(1, "M01", f"file month {m.group(1)}-{m.group(2)} differs from prepared {prepared}")

    def section(title: str, level: str = "##") -> int | None:
        for i, line in enumerate(lines):
            if re.match(rf"^{level}\s+{re.escape(title)}\s*$", line):
                return i
        return None

    companies: dict[str, int] = {}
    kinds: set[str] = set()
    s = section("Companies")
    if s is None:
        err(1, "M04", "missing '## Companies' table")
    else:
        for n, cells in table_rows(lines, s + 1):
            if len(cells) < 3:
                err(n, "M04", "company row needs: #, Company, Kind, Why included")
                continue
            name, kind = cells[1], cells[2].lower()
            companies[name.lower()] = n
            if kind not in KINDS:
                err(n, "M04", f"kind '{cells[2]}' is not one of {', '.join(sorted(KINDS))}")
            kinds.add(kind)
        if not 10 <= len(companies) <= 30:
            err(s + 1, "M04", f"{len(companies)} companies; cover 10 to 30")
        if not kinds & {"incumbent", "workaround"}:
            warn(s + 1, "M14", "no company of kind incumbent or workaround (what customers use today)")
        if "top-tier" not in kinds:
            warn(s + 1, "M14", "no company of kind top-tier (the level the product wants to reach)")

    facts: dict[str, tuple[int, str]] = {}
    priced: set[str] = set()
    s = section("Facts")
    if s is None:
        err(1, "M05", "missing '## Facts' table")
    else:
        rows = table_rows(lines, s + 1)
        for n, cells in rows:
            if len(cells) < 7:
                err(n, "M05", "fact row needs: ID, Company, Field, Fact, Source, Accessed, Label")
                continue
            fid, comp, field, fact, src, acc, label = cells[:7]
            label = label.lower()
            if not FACT_ID_RE.fullmatch(fid):
                err(n, "M05", f"fact ID '{fid}' must look like F001")
            facts[fid] = (n, label)
        for n, cells in rows:
            if len(cells) < 7:
                continue
            fid, comp, field, fact, src, acc, label = cells[:7]
            label, field = label.lower(), field.lower()
            if comp.lower() not in companies:
                err(n, "M10", f"company '{comp}' is not in the companies table")
            if field not in FIELDS:
                warn(n, "M05", f"field '{field}' is not one of the known fields")
            if not re.match(r"^<?https://\S+>?$", src):
                err(n, "M05", f"{fid}: source must be one https URL")
            d = parse_date(acc)
            if d is None:
                err(n, "M05", f"{fid}: accessed must be YYYY-MM-DD")
            elif d > today:
                err(n, "M05", f"{fid}: accessed {d} is in the future")
            elif prepared and d < prepared - dt.timedelta(days=45):
                warn(n, "M13", f"{fid}: read {d}, more than 45 days before prepared {prepared}; read it again")
            if label not in LABELS:
                err(n, "M05", f"{fid}: label must be verified, reported or inferred")
            if label == "inferred":
                m = re.search(r"\bfrom\s+(F\d{3}(?:\s*(?:,|and)\s*F\d{3})*)", fact)
                basis = FACT_ID_RE.findall(m.group(1)) if m else []
                if not basis or any(b not in facts for b in basis):
                    err(n, "M06", f"{fid}: inferred fact must name existing basis facts ('from F012')")
            if field == "pricing":
                priced.add(comp.lower())
                if not NOT_PUBLIC_RE.search(fact):
                    if not (CURRENCY_RE.search(fact) and PERIOD_RE.search(fact)):
                        err(n, "M11", f"{fid}: price needs a currency and a billing period")
                    elif not NETGROSS_RE.search(fact):
                        warn(n, "M12", f"{fid}: say whether the price is net or gross")
        for name, n in companies.items():
            if name not in priced:
                err(n, "M07", f"no pricing fact for '{name}'; write 'not public' with the page you checked")

    syn = section("Synthesis")
    if syn is None:
        err(1, "M08", "missing '## Synthesis'")
    for title in SECTIONS:
        i = section(title, "###")
        if i is None:
            err(syn + 1 if syn is not None else 1, "M08", f"missing '### {title}'")
            continue
        body = []
        for line in lines[i + 1:]:
            if re.match(r"^#{2,3}\s", line):
                break
            if line.strip():
                body.append(line)
        if not body:
            err(i + 1, "M08", f"'### {title}' is empty")
        if title == "Recommendations":
            items: list[tuple[int, str]] = []
            j = i + 1
            while j < len(lines) and not re.match(r"^#{2,3}\s", lines[j]):
                if re.match(r"^\d+\.\s", lines[j]):
                    block = [lines[j]]
                    k = j + 1
                    while k < len(lines) and lines[k].startswith((" ", "\t")) and lines[k].strip():
                        block.append(lines[k])
                        k += 1
                    items.append((j + 1, " ".join(block)))
                j += 1
            if not items:
                err(i + 1, "M09", "recommendations must be a numbered list")
            for n, item in items:
                m = re.search(r"Evidence:\s*(.+)$", item)
                ids = FACT_ID_RE.findall(m.group(1)) if m else []
                if not ids:
                    err(n, "M09", "recommendation without 'Evidence: F0xx'")
                    continue
                unknown = [x for x in ids if x not in facts]
                if unknown:
                    err(n, "M09", f"evidence {', '.join(unknown)} not in the facts table")
                elif all(facts[x][1] == "inferred" for x in ids):
                    warn(n, "M15", "recommendation rests only on inferred facts")
    return out


def run(path: str, today: dt.date) -> int:
    text = Path(path).read_text(encoding="utf-8")
    findings = check(path, text, today)
    for n, level, code, msg in findings:
        print(f"{path}:{n}: {level} {code} {msg}")
    errors = sum(1 for f in findings if f[1] == "error")
    print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


def fixture(n_companies: int = 10) -> str:
    kinds = ["incumbent", "top-tier"] + ["direct"] * 28
    comp = "\n".join(f"| {i + 1} | Co{i + 1} | {kinds[i]} | reason |" for i in range(n_companies))
    facts = "\n".join(
        f"| F{i + 1:03d} | Co{i + 1} | pricing | Team 12 EUR per user per month, billed annually, net |"
        f" https://co{i + 1}.example.com/pricing | 2026-11-02 | verified |"
        for i in range(n_companies)
    )
    syn = "\n\n".join(f"### {t}\n\ntext" for t in SECTIONS if t != "Recommendations")
    return f"""# Market analysis

prepared: 2026-11-03
valid_until: 2027-03-31

## Companies

| # | Company | Kind | Why included |
|---|---|---|---|
{comp}

## Facts

| ID | Company | Field | Fact | Source | Accessed | Label |
|---|---|---|---|---|---|---|
{facts}
| F900 | Co1 | limits | about 20 users at most, from F001 | https://co1.example.com/pricing | 2026-11-02 | inferred |

## Synthesis

### Recommendations

1. Price the team plan inside the corridor. Evidence: F001, F002

{syn}
"""


def self_test() -> int:
    name = "docs/business/market-analysis-2026-11.md"
    today = dt.date(2026, 11, 3)
    cases = [
        ("valid", fixture(), set()),
        ("expired", fixture(), {"M03"}),
        ("too few", fixture(9), {"M04"}),
        ("no source", fixture().replace("https://co3.example.com/pricing", "memory"), {"M05"}),
        ("bad label", fixture().replace("| 2026-11-02 | verified |", "| 2026-11-02 | guess |", 1), {"M05"}),
        ("inferred no basis", fixture().replace(", from F001", ""), {"M06"}),
        ("no currency", fixture().replace("Team 12 EUR per user", "Team 12 per user", 1), {"M11"}),
        ("no evidence", fixture().replace(" Evidence: F001, F002", ""), {"M09"}),
        ("unknown evidence", fixture().replace("Evidence: F001, F002", "Evidence: F777"), {"M09"}),
        ("short validity", fixture().replace("valid_until: 2027-03-31", "valid_until: 2026-12-31"), {"M02"}),
        ("missing section", fixture().replace("### Threats\n\ntext", ""), {"M08"}),
        ("not public ok", fixture().replace("Team 12 EUR per user per month, billed annually, net",
                                            "not public; pricing page asks for a demo", 1), set()),
    ]
    failed = 0
    for label, text, expect in cases:
        day = dt.date(2027, 4, 1) if label == "expired" else today
        codes = {c for _, lvl, c, _ in check(name, text, day) if lvl == "error"}
        ok = codes == expect
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}: expected {sorted(expect) or 'none'}, got {sorted(codes) or 'none'}")
    if {c for _, lvl, c, _ in check("notes.md", fixture(), today) if lvl == "error"} != {"M01"}:
        print("FAIL file name")
        failed += 1
    else:
        print("ok   file name")
    return 1 if failed else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?")
    p.add_argument("--today", help="YYYY-MM-DD, default: the current date")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        p.error("path required")
    today = parse_date(a.today) if a.today else dt.date.today()
    if today is None:
        p.error("--today must be YYYY-MM-DD")
    return run(a.path, today)


if __name__ == "__main__":
    sys.exit(main())
