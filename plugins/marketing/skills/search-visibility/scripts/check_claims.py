#!/usr/bin/env python3
"""Check a claims table: every product claim on a page traces to a file and line or a dated record.

The table is Markdown with the columns claim | value as on page | source | checked on (template in
assets/claims-table.md). Per row:
  - source `path:12` or `path:12-14` (also `path#L12`): the file exists under --root, the line exists, and the
    value appears within two lines of the cited line or range;
  - source with an ISO date and no file:line (a dated record, e.g. "record 2026-10-30: support export"): accepted;
  - no source, a source that is another marketing page (site, content, blog or locale files, *.html, *.mdx,
    the page itself, a URL on --own-host): the row fails;
  - checked on: an ISO date, not in the future;
  - with --page: the value appears on the page after tags are stripped.
Python 3.10 or later, standard library only. Reads files, writes nothing.

Usage:
  check_claims.py --table docs/claims/pricing.md [--root .] [--page site/pricing.html] [--own-host www.example.com]
                  [--marketing GLOB ...] [--json]
  check_claims.py --self-test

Exit codes:
  0  every row passes
  1  at least one row fails, or the table has no rows (or a failed self-test)
  2  usage error: table, root or page missing, or no claims table in the file
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path, PurePosixPath

TOOL = "check_claims.py 1.0"
WINDOW = 2
MARKETING_DIRS = {"pages", "content", "blog", "marketing", "landing", "website", "site", "www", "public", "dist",
                  "static", "locales", "locale", "lang", "i18n", "translations"}
MARKETING_EXT = {".html", ".htm", ".mdx"}
EMPTY_SOURCES = {"", "-", "n/a", "na", "none", "todo", "tbd", "?"}
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
FILE_LINE_RE = re.compile(r"^(?P<path>[^\s:#]+?)(?::(?P<a>\d+)(?:-(?P<b>\d+))?|#L(?P<c>\d+)(?:-L?(?P<d>\d+))?)$")


class UsageError(Exception):
    code = 2


def norm(s: str) -> str:
    s = s.replace(" ", " ").replace(" ", " ").replace(" ", " ")
    s = re.sub(r"(?<=\d)[,.' ](?=\d{3}(?!\d))", "", s)  # 1,000 / 1.000 / 1 000 -> 1000
    return " ".join(s.split()).casefold()


def contains(hay: str, needle: str) -> bool:
    """Whole-token match of a normalised value: '10' is not found in '1000'."""
    if not needle:
        return False
    pre = r"(?<![^\W_])" if needle[0].isalnum() else ""
    post = r"(?![^\W_])" if needle[-1].isalnum() else ""
    return re.search(pre + re.escape(needle) + post, hay) is not None


def strip_cell(c: str) -> str:
    c = c.strip()
    if len(c) >= 2 and c[0] == c[-1] and c[0] in "`\"'":
        c = c[1:-1].strip()
    return c


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", body)]


def parse_table(text: str) -> list[dict] | None:
    """Return the rows of the first table whose header starts claim | value ... | source | checked."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|") or i + 1 >= len(lines):
            continue
        head = [h.lower() for h in split_row(line)]
        if len(head) < 4 or not head[0].startswith("claim") or not head[1].startswith("value"):
            continue
        if not any(h.startswith("source") for h in head) or not any(h.startswith("checked") for h in head):
            continue
        if not re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            continue
        si = next(k for k, h in enumerate(head) if h.startswith("source"))
        ci = next(k for k, h in enumerate(head) if h.startswith("checked"))
        rows = []
        for n in range(i + 2, len(lines)):
            if not lines[n].lstrip().startswith("|"):
                break
            cells = split_row(lines[n]) + [""] * len(head)
            rows.append({"line": n + 1, "claim": strip_cell(cells[0]), "value": strip_cell(cells[1]),
                         "source": strip_cell(cells[si]), "checked_on": strip_cell(cells[ci])})
        return rows
    return None


def page_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return norm(html.unescape(raw))


def is_marketing_path(rel: str, page_rel: str | None, extra: list[str]) -> bool:
    p = PurePosixPath(rel)
    if page_rel and p == PurePosixPath(page_rel):
        return True
    if p.suffix.lower() in MARKETING_EXT:
        return True
    if any(part.lower() in MARKETING_DIRS for part in p.parts[:-1]):
        return True
    return any(fnmatch.fnmatch(rel, g) for g in extra)


def check_row(row: dict, root: Path, page_norm: str | None, page_rel: str | None, own_hosts: set[str],
              extra: list[str], today: dt.date) -> list[str]:
    problems: list[str] = []
    value, src = row["value"], row["source"]
    if not row["claim"]:
        problems.append("no claim text")
    if not value:
        problems.append("no value as on page")
    # checked on
    m = re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["checked_on"])
    if not m:
        problems.append(f"checked on '{row['checked_on']}' is not an ISO date (YYYY-MM-DD)")
    else:
        try:
            if dt.date.fromisoformat(row["checked_on"]) > today:
                problems.append(f"checked on {row['checked_on']} is in the future")
        except ValueError:
            problems.append(f"checked on '{row['checked_on']}' is not a valid date")
    # page
    if page_norm is not None and value and not contains(page_norm, norm(value)):
        problems.append(f"value '{value}' does not appear on the page")
    # source
    if src.lower() in EMPTY_SOURCES:
        problems.append("no source: cite file:line or a dated record, or remove the claim from the page")
        return problems
    if re.match(r"^https?://", src, re.I):
        host = (urllib.parse.urlsplit(src.split()[0]).hostname or "").lower()
        if host in own_hosts:
            problems.append(f"source is a page on the own site ({host}); cite the code, config or spec behind it")
        elif not DATE_RE.search(src):
            problems.append("external URL without a read date; add one, e.g. '(read 2026-10-30)'")
        return problems
    fm = FILE_LINE_RE.match(src)
    if not fm:
        if DATE_RE.search(src):
            return problems  # dated record
        problems.append(f"source '{src}' is neither file:line nor a dated record")
        return problems
    rel = fm.group("path")
    start = int(fm.group("a") or fm.group("c"))
    end = int(fm.group("b") or fm.group("d") or start)
    if rel.startswith("/") or re.match(r"^[A-Za-z]:", rel) or ".." in PurePosixPath(rel).parts:
        problems.append(f"source path '{rel}' must be relative to the repository root, without '..'")
        return problems
    if is_marketing_path(rel, page_rel, extra):
        problems.append(f"source '{rel}' is a marketing page or copy file; another page is never the source")
        return problems
    path = (root / rel).resolve()
    if root not in path.parents or not path.is_file():
        problems.append(f"source file '{rel}' does not exist under the repository root")
        return problems
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if end < start or start < 1 or end > len(lines):
        problems.append(f"cited line {start}{'-' + str(end) if end != start else ''} is outside '{rel}' "
                        f"({len(lines)} lines)")
        return problems
    lo, hi = max(1, start - WINDOW), min(len(lines), end + WINDOW)
    window = norm(" ".join(lines[lo - 1:hi]))
    if value and not contains(window, norm(value)):
        cited = lines[start - 1].strip()
        problems.append(f"'{rel}' lines {lo}-{hi} do not contain '{value}'; line {start} reads: "
                        f"{cited[:120]!r}")
    return problems


def check_table(table: Path, root: Path, page: Path | None, own_hosts: set[str], extra: list[str],
                today: dt.date) -> dict:
    if not table.is_file():
        raise UsageError(f"table {table} not found")
    if not root.is_dir():
        raise UsageError(f"--root {root} is not a directory")
    root = root.resolve()
    rows = parse_table(table.read_text(encoding="utf-8", errors="replace"))
    if rows is None:
        raise UsageError(f"no claims table in {table}: need a header 'claim | value as on page | source | checked on'")
    page_norm = page_rel = None
    if page is not None:
        if not page.is_file():
            raise UsageError(f"--page {page} not found")
        page_norm = page_text(page)
        try:
            page_rel = page.resolve().relative_to(root).as_posix()
        except ValueError:
            page_rel = None
    results = []
    for r in rows:
        probs = check_row(r, root, page_norm, page_rel, own_hosts, extra, today)
        results.append({**r, "ok": not probs, "problems": probs})
    failed = sum(1 for r in results if not r["ok"])
    code = 1 if failed or not results else 0
    return {"tool": TOOL, "table": table.as_posix(), "rows": len(results), "failed": failed, "exit": code,
            "results": results, **({"note": "the table has no rows"} if not results else {})}


def render_text(rep: dict) -> str:
    out = []
    for r in rep["results"]:
        out.append(f"{rep['table']}:{r['line']} {'OK  ' if r['ok'] else 'FAIL'} {r['claim']} = \"{r['value']}\"")
        for p in r["problems"]:
            out.append(f"    - {p}")
    if not rep["results"]:
        out.append(f"{rep['table']}: the claims table has no rows; a page with product claims needs one row each")
    out.append(f"Summary: {rep['rows']} row(s), {rep['failed']} failed. Exit {rep['exit']}.")
    return "\n".join(out)


# --- self-test -----------------------------------------------------------------------------------------

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "claims"


def self_test() -> int:
    fails: list[str] = []
    check = lambda ok, msg: ok or fails.append(msg)  # noqa: E731
    today = dt.date(2026, 11, 4)
    try:
        good = check_table(FIXTURES / "claims-good.md", FIXTURES, FIXTURES / "site" / "pricing.html",
                           {"www.example.com"}, [], today)
        check(good["exit"] == 0 and good["failed"] == 0,
              f"good table must pass: {[r['problems'] for r in good['results'] if not r['ok']]}")
        check(good["rows"] == 5, f"good table: expected 5 rows, got {good['rows']}")

        bad = check_table(FIXTURES / "claims-bad.md", FIXTURES, FIXTURES / "site" / "pricing.html",
                          {"www.example.com"}, ["docs/press/*"], today)
        by = {r["claim"]: r for r in bad["results"]}
        expect = {
            "Seats on Team": "do not contain",
            "Data retention": "no source",
            "Uptime": "marketing page",
            "Press quote": "marketing page",
            "Customer count": "own site",
            "Locations": "does not exist",
            "API rate limit": "outside",
            "Webhook retries": "neither file:line",
            "SSO": "not an ISO date",
            "Audit log": "in the future",
            "Escape": "without '..'",
            "Status pages": "does not appear on the page",
            "Vendor price": "without a read date",
            "Window edge": "do not contain",
            "Template copy": "marketing page",
        }
        for claim, needle in expect.items():
            r = by.get(claim)
            check(r is not None and not r["ok"] and any(needle in p for p in r["problems"]),
                  f"row '{claim}' must fail with '{needle}': {r and r['problems']}")
        check(bad["exit"] == 1 and bad["failed"] == len(expect), f"bad table: {bad['failed']} failed, exit {bad['exit']}")
        check(by.get("Window inside") is not None and by["Window inside"]["ok"],
              f"value two lines below the cited line must pass: {by.get('Window inside')}")
        check(bad["rows"] == len(expect) + 1, f"bad table rows {bad['rows']}")

        empty = check_table(FIXTURES / "claims-empty.md", FIXTURES, None, set(), [], today)
        check(empty["exit"] == 1 and empty["rows"] == 0, "a table without rows must exit 1")
        for args in ((FIXTURES / "site" / "pricing.html", FIXTURES, None), (FIXTURES / "missing.md", FIXTURES, None),
                     (FIXTURES / "claims-good.md", FIXTURES / "nope", None),
                     (FIXTURES / "claims-good.md", FIXTURES, FIXTURES / "missing.html")):
            try:
                check_table(args[0], args[1], args[2], set(), [], today)
                fails.append(f"usage error expected for {args}")
            except UsageError:
                pass
        check(norm("1,000") == norm("1000") == norm("1.000") == norm("1 000"), "digit-group separators")
        check(norm("1.5 GB") != norm("15 GB") and norm("19,00") == "19,00", "decimals must stay")
        check("|" in split_row(r"| a \| b | c |")[0], "escaped pipes stay in the cell")
        check(not contains(norm("services: 1000"), norm("10")) and contains(norm("seats: 10,"), norm("10")),
              "values match whole tokens only")
        text = render_text(bad)
        check("FAIL Seats on Team" in text and "Exit 1." in text, "text output names failing rows and the exit")
    except Exception as e:  # a crash is a failure, reported like one
        fails.append(f"unexpected {e.__class__.__name__}: {e}")
    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("check_claims.py self-test: ok (file:line window, missing source, marketing sources, own-host URL, "
          "missing file, line range, dated record, dates, traversal, page text, empty table, usage errors)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="check_claims.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", help="Markdown file with the claims table")
    ap.add_argument("--root", default=".", help="repository root that file:line sources are relative to")
    ap.add_argument("--page", help="page file whose text must contain every value")
    ap.add_argument("--own-host", action="append", default=[], help="host of the own site; URLs on it fail")
    ap.add_argument("--marketing", action="append", default=[], help="extra glob of marketing files, e.g. docs/press/*")
    ap.add_argument("--today", help=argparse.SUPPRESS)
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--self-test", action="store_true", help="run offline checks against scripts/fixtures and exit")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        if not args.table:
            raise UsageError("--table is required")
        today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
        rep = check_table(Path(args.table), Path(args.root), Path(args.page) if args.page else None,
                          {h.lower() for h in args.own_host}, args.marketing, today)
    except UsageError as e:
        print(json.dumps({"error": str(e), "exit": 2}), file=sys.stderr)
        return 2
    print(json.dumps(rep, indent=1, ensure_ascii=False) if args.json else render_text(rep))
    return rep["exit"]


if __name__ == "__main__":
    sys.exit(main())
