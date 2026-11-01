#!/usr/bin/env python3
"""Check a project's inception docs: skeleton, headers, routing table, approval and drift hints.

Usage:
  check_docs.py [ROOT] [--docs DIR] [--require-approved] [--changed FILE] [--strict]
  check_docs.py --self-test

ROOT defaults to the current directory. DIR is the docs folder relative to ROOT (default: docs).

Checks (code, level, what fails):
  C01 error    the docs folder is missing
  C02 error    a required part is missing: PROJECT-FACTS.md, a .md file in product/, business/,
               specs/ and adr/, or a plans/*inception*.md record
  C03 error    no routing file: AGENTS.md, CLAUDE.md or .claude/CLAUDE.md at ROOT
  C04 error    no routing file has a table with a "Read first" column
  C05 error    a path in a routing table does not exist
  C06 warning  a spec under specs/ is not named in any routing table (error with --strict)
  C07 error    AGENTS.md holds the routing table, a CLAUDE.md exists, and no CLAUDE.md imports
               @AGENTS.md outside code spans (Claude Code then reads only CLAUDE.md)
  C08 warning  a routing file is over 200 lines
  C09 error    a document in product/, business/ or specs/ has no "Status:" or "Skills:" header line
  C10 error    an entry on a "Code:" header line matches no file or folder under ROOT
  C11 error    a "Code:" header names paths but "Checked against code:" has no YYYY-MM-DD date
  C12 error    the inception record has no Status line, or Open decisions is missing, or an item
               has no "Recommendation:", "Decision:" or "Answer:" line (a "None:" line is fine)
  C13 error    --require-approved and the inception record is not "Status: Approved" with
               "Approved-by:" filled
  C14 error    two ADR files share a number
  C15 warning  --changed lists a file under a spec's Code: paths but not the spec itself
               (error with --strict)

--changed FILE reads one changed path per line, relative to ROOT; "-" reads stdin. In CI:
  git diff --name-only origin/main...HEAD | python3 check_docs.py --changed -

Output: one finding per line as "path:line: level code message". Exit 0 when there is no error
(and, with --strict, no warning), 1 otherwise, 2 on a usage error. Python 3.8 or later, standard
library only, no network.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import tempfile
from pathlib import Path

ROUTING_CANDIDATES = ["AGENTS.md", "CLAUDE.md", ".claude/CLAUDE.md"]
HEADER_KEYS = ["status", "skills", "owner", "code", "checked against code", "approved-by", "mode"]
HEADER_SCAN_LINES = 25
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
IMPORT_RE = re.compile(r"(?:^|\s)@(?:\./|\.\./)?AGENTS\.md\b")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\]\(([^)\s]+)")
TICK_RE = re.compile(r"`([^`]+)`")
ADR_RE = re.compile(r"^(\d{3,5})-")


class Finding:
    def __init__(self, path: str, line: int, level: str, code: str, msg: str) -> None:
        self.path, self.line, self.level, self.code, self.msg = path, line, level, code, msg

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.level} {self.code} {self.msg}"


def read(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []


def headers(lines: list[str]) -> dict[str, tuple[int, str]]:
    """Header lines such as 'Status: Draft', '- Skills: x' or '**Code:** src/x'."""
    out: dict[str, tuple[int, str]] = {}
    for i, raw in enumerate(lines[:HEADER_SCAN_LINES]):
        line = raw.replace("**", "").strip()
        line = re.sub(r"^(?:[-*>]\s+)+", "", line)
        m = re.match(r"^([A-Za-z][A-Za-z -]*?)\s*:\s*(.*)$", line)
        if m and m.group(1).strip().lower() in HEADER_KEYS:
            key = m.group(1).strip().lower()
            out.setdefault(key, (i + 1, m.group(2).strip()))
    return out


def md_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*.md") if p.is_file()) if folder.is_dir() else []


def rel(root: Path, p: Path) -> str:
    try:
        return p.relative_to(root).as_posix()
    except ValueError:
        return p.as_posix()


def tables(lines: list[str]) -> list[tuple[int, list[str], list[tuple[int, str]]]]:
    """Markdown tables as (header line number, header cells, body rows)."""
    found = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|?\s*:?-{3,}", lines[i + 1]
        ):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            body = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                body.append((j + 1, lines[j]))
                j += 1
            found.append((i + 1, head, body))
            i = j
        else:
            i += 1
    return found


def path_candidates(cell_text: str) -> list[str]:
    cands = [m.group(1) for m in TICK_RE.finditer(cell_text)]
    cands += [m.group(1) for m in LINK_RE.finditer(cell_text)]
    out = []
    for c in cands:
        c = c.strip().lstrip("@")
        if not c or " " in c or "://" in c or c.startswith(("mailto:", "#", "/")):
            continue
        if "[" in c or "YYYY" in c or "NNNN" in c:
            continue  # a naming pattern, not a file
        c = c.split("#", 1)[0]
        c = re.sub(r":\d+(?:-\d+)?$", "", c)  # path:line
        if "/" in c or c.endswith(".md"):
            out.append(c)
    return out


def exists_any(root: Path, base: Path, item: str) -> bool:
    for anchor in (root, base):
        try:
            if any(ch in item for ch in "*?["):
                if any(anchor.glob(item)):
                    return True
            elif (anchor / item).exists():
                return True
        except (NotImplementedError, ValueError, OSError):
            return False
    return False


def code_entries(value: str) -> list[str]:
    if value.strip().lower().startswith(("none", "n/a", "-")) or not value.strip():
        return []
    items = [v.strip().strip("`").strip() for v in value.split(",")]
    return [v for v in items if v and not v.lower().startswith("none")]


def matches(pattern: str, path: str) -> bool:
    pattern = pattern.rstrip("/")
    return fnmatch.fnmatch(path, pattern) or path.startswith(pattern + "/") or path == pattern


def check(
    root: Path,
    docs_name: str = "docs",
    require_approved: bool = False,
    changed: list[str] | None = None,
    strict: bool = False,
) -> list[Finding]:
    f: list[Finding] = []
    warn = "error" if strict else "warning"
    docs = root / docs_name
    d = rel(root, docs)

    if not docs.is_dir():
        f.append(Finding(d, 0, "error", "C01", f"docs folder '{d}' is missing"))
        return f

    # C02 skeleton
    if not (docs / "PROJECT-FACTS.md").is_file():
        f.append(Finding(f"{d}/PROJECT-FACTS.md", 0, "error", "C02", "PROJECT-FACTS.md is missing"))
    for part in ("product", "business", "specs", "adr"):
        if not md_files(docs / part):
            f.append(Finding(f"{d}/{part}/", 0, "error", "C02", f"{part}/ has no .md file"))
    records = sorted((docs / "plans").glob("*inception*.md")) if (docs / "plans").is_dir() else []
    if not records:
        f.append(Finding(f"{d}/plans/", 0, "error", "C02", "no plans/*inception*.md record"))

    # C09-C11 headers of product, business and spec documents
    spec_code: dict[str, list[str]] = {}
    for part in ("product", "business", "specs"):
        for p in md_files(docs / part):
            if p.name.lower() == "readme.md":
                continue
            r = rel(root, p)
            h = headers(read(p))
            for key in ("status", "skills"):
                if key not in h or not h[key][1]:
                    f.append(Finding(r, 1, "error", "C09", f"no '{key.capitalize()}:' header line"))
            if "code" in h:
                line, value = h["code"]
                entries = code_entries(value)
                for e in entries:
                    if not exists_any(root, p.parent, e):
                        f.append(Finding(r, line, "error", "C10", f"Code: '{e}' matches nothing; spec or code drifted"))
                if entries:
                    checked = h.get("checked against code", (line, ""))
                    if not DATE_RE.search(checked[1]):
                        f.append(Finding(r, checked[0], "error", "C11", "Code: is set but 'Checked against code:' has no date"))
                    if part == "specs":
                        spec_code[r] = entries

    # C03-C08 routing
    routing = [root / c for c in ROUTING_CANDIDATES if (root / c).is_file()]
    if not routing:
        f.append(Finding("AGENTS.md", 0, "error", "C03", "no AGENTS.md or CLAUDE.md at the project root"))
    referenced: set[str] = set()
    table_in: set[str] = set()
    for rf in routing:
        lines = read(rf)
        r = rel(root, rf)
        if len(lines) > 200:
            f.append(Finding(r, 201, "warning", "C08", f"{len(lines)} lines; keep the routing file under 200"))
        for hline, head, body in tables(lines):
            if not any("read first" in c.lower() for c in head):
                continue
            table_in.add(r)
            for n, row in body:
                for c in path_candidates(row):
                    if exists_any(root, rf.parent, c):
                        for anchor in (root, rf.parent):
                            if (anchor / c).exists():
                                referenced.add(rel(root, anchor / c))
                                break
                    else:
                        f.append(Finding(r, n, "error", "C05", f"routing table points at '{c}', which does not exist"))
    if routing and not table_in:
        f.append(Finding(rel(root, routing[0]), 1, "error", "C04", "no table with a 'Read first' column"))

    claude_files = [p for p in routing if p.name == "CLAUDE.md"]
    if "AGENTS.md" in table_in and claude_files and not any(t.endswith("CLAUDE.md") for t in table_in):
        imported = False
        for cf in claude_files:
            fence = False
            for line in read(cf):
                if line.lstrip().startswith(("```", "~~~")):
                    fence = not fence
                    continue
                if not fence and IMPORT_RE.search(CODE_SPAN_RE.sub("", line)):
                    imported = True
        if not imported:
            f.append(Finding(rel(root, claude_files[0]), 1, "error", "C07",
                             "CLAUDE.md exists but does not import @AGENTS.md; Claude Code will not read the routing table"))

    # C06 orphan specs
    if table_in:
        for p in md_files(docs / "specs"):
            r = rel(root, p)
            if p.name.lower() != "readme.md" and r not in referenced:
                f.append(Finding(r, 1, warn, "C06", "spec is not named in the routing table"))

    # C12-C13 inception record
    if records:
        rec = records[-1]
        r = rel(root, rec)
        lines = read(rec)
        h = headers(lines)
        status = h.get("status", (1, ""))[1]
        if not re.match(r"(?i)(draft|approved|superseded)\b", status):
            f.append(Finding(r, h.get("status", (1, ""))[0], "error", "C12", "no 'Status: Draft|Approved|Superseded' line"))
        start = next((i for i, l in enumerate(lines) if re.match(r"^#{2,3}\s+(?:\d+\.\s+)?Open decisions", l, re.I)), None)
        if start is None:
            f.append(Finding(r, 1, "error", "C12", "no 'Open decisions' section"))
        else:
            end = next((i for i in range(start + 1, len(lines)) if re.match(r"^#{1,3}\s", lines[i])), len(lines))
            block = lines[start + 1:end]
            items = [i for i, l in enumerate(block) if re.match(r"^\d+\.\s", l)]
            if not items and not any(re.match(r"^\s*None:", l) for l in block):
                f.append(Finding(r, start + 1, "error", "C12", "Open decisions has no numbered item and no 'None:' line"))
            for k, i in enumerate(items):
                j = items[k + 1] if k + 1 < len(items) else len(block)
                text = "\n".join(block[i:j])
                if not re.search(r"(Recommendation|Decision|Answer)\s*:", text):
                    f.append(Finding(r, start + 2 + i, "error", "C12", "decision has no 'Recommendation:' line"))
        if require_approved:
            by = h.get("approved-by", (1, ""))[1]
            if not status.lower().startswith("approved") or not by or by.startswith("["):
                f.append(Finding(r, h.get("status", (1, ""))[0], "error", "C13",
                                 "inception is not approved (needs 'Status: Approved' and 'Approved-by:')"))

    # C14 ADR numbers
    seen: dict[str, str] = {}
    for p in md_files(docs / "adr"):
        m = ADR_RE.match(p.name)
        if m:
            num = m.group(1).lstrip("0") or "0"
            if num in seen:
                f.append(Finding(rel(root, p), 1, "error", "C14", f"ADR number {m.group(1)} is also used by {seen[num]}"))
            else:
                seen[num] = rel(root, p)

    # C15 code changed without its spec
    if changed is not None:
        changed_set = set()
        for c in changed:
            c = c.strip()
            if c:
                changed_set.add(c[2:] if c.startswith("./") else c)
        for spec, entries in spec_code.items():
            if spec in changed_set:
                continue
            hit = sorted(c for c in changed_set if any(matches(e, c) for e in entries))
            if hit:
                f.append(Finding(spec, 1, warn, "C15",
                                 f"code under this spec changed ({', '.join(hit[:3])}) but the spec did not; update it or say why"))
    return f


# ---------------------------------------------------------------- self-test

GOOD = {
    "AGENTS.md": "# Agents\n\n| Task | Read first |\n|---|---|\n| Billing | `docs/specs/billing.md` |\n"
    "| Product | [brief](docs/product/brief.md) |\n| New plan | `docs/plans/YYYY-MM-DD-[slug].md` |\n",
    "docs/PROJECT-FACTS.md": "# Project facts\n",
    "docs/product/brief.md": "# Brief\n\nStatus: Approved\nSkills: product-strategy\n",
    "docs/business/model.md": "# Model\n\n- Status: Draft\n- Skills: pricing-and-unit-economics\n",
    "docs/specs/billing.md": "# Billing\n\n**Status:** Approved\n**Skills:** billing-eu-b2b\n"
    "**Code:** src/billing/**, src/invoice.ts\n**Checked against code:** 2026-03-04\n",
    "docs/adr/0001-record-decisions.md": "# 1. Record decisions\n",
    "docs/plans/2026-03-01-inception.md": "# Inception\n\nStatus: Approved\nApproved-by: Owner, 2026-03-02\n\n"
    "## Open decisions\n1. Region?\n   - Recommendation: EU, because ...\n",
    "src/billing/run.ts": "export {}\n",
    "src/invoice.ts": "export {}\n",
}


def build(base: Path, files: dict[str, str | None]) -> Path:
    for name, body in files.items():
        if body is None:
            continue
        p = base / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return base


def codes(findings: list[Finding], level: str | None = None) -> set[str]:
    return {x.code for x in findings if level is None or x.level == level}


def self_test() -> int:
    cases = []

    def case(name, overrides, expect, absent=(), **kw):
        cases.append((name, overrides, set(expect), set(absent), kw))

    case("good tree passes", {}, [], ["C01", "C02", "C05", "C06", "C07", "C09", "C10", "C11", "C12", "C13"],
         require_approved=True)
    case("missing business doc", {"docs/business/model.md": None}, ["C02"])
    case("missing inception record", {"docs/plans/2026-03-01-inception.md": None}, ["C02"])
    case("no routing file", {"AGENTS.md": None}, ["C03"])
    case("routing without Read first column", {"AGENTS.md": "| Task | Spec |\n|---|---|\n| x | `docs/specs/billing.md` |\n"}, ["C04"])
    case("broken routing path", {"AGENTS.md": GOOD["AGENTS.md"] + "| Auth | `docs/specs/auth.md` |\n"}, ["C05"])
    case("orphan spec", {"docs/specs/tenancy.md": "Status: Draft\nSkills: tenant-isolation\n"}, ["C06"])
    case("CLAUDE.md without import", {"CLAUDE.md": "# Notes\n\nRun tests in the container.\n"}, ["C07"])
    case("import inside a code span does not count", {"CLAUDE.md": "Mention `@AGENTS.md` here.\n"}, ["C07"])
    case("CLAUDE.md imports AGENTS.md", {"CLAUDE.md": "@AGENTS.md\n\nRun tests in the container.\n"}, [], ["C07"])
    case("long routing file", {"AGENTS.md": GOOD["AGENTS.md"] + "x\n" * 210}, ["C08"])
    case("spec without Skills header", {"docs/specs/billing.md": "Status: Draft\nCode: src/invoice.ts\nChecked against code: 2026-03-04\n"}, ["C09"])
    case("Code path that no longer exists", {"docs/specs/billing.md": GOOD["docs/specs/billing.md"].replace("src/invoice.ts", "src/old.ts")}, ["C10"])
    case("Code without a check date", {"docs/specs/billing.md": "Status: Draft\nSkills: billing-eu-b2b\nCode: src/invoice.ts\n"}, ["C11"])
    case("Code: none yet needs no date", {"docs/specs/billing.md": "Status: Draft\nSkills: billing-eu-b2b\nCode: none yet\n"}, [], ["C10", "C11"])
    case("decision without recommendation", {"docs/plans/2026-03-01-inception.md": "Status: Draft\n\n## Open decisions\n1. Region?\n   - Options: A, B\n"}, ["C12"])
    case("decisions None: is fine", {"docs/plans/2026-03-01-inception.md": "Status: Draft\n\n## Open decisions\nNone: all settled in ADRs.\n"}, [], ["C12"])
    case("draft fails the approval gate", {"docs/plans/2026-03-01-inception.md": "Status: Draft\nApproved-by:\n\n## Open decisions\nNone: settled.\n"}, ["C13"], require_approved=True)
    case("duplicate ADR number", {"docs/adr/0001-other.md": "# 1. Other\n"}, ["C14"])
    case("code changed without spec", {}, ["C15"], changed=["src/billing/run.ts"])
    case("code changed with spec", {}, [], ["C15"], changed=["src/billing/run.ts", "docs/specs/billing.md"])
    case("strict turns orphan warning into error", {"docs/specs/tenancy.md": "Status: Draft\nSkills: tenant-isolation\n"}, ["C06"], strict=True)

    failed = 0
    for name, overrides, expect, absent, kw in cases:
        with tempfile.TemporaryDirectory() as tmp:
            files = dict(GOOD)
            files.update(overrides)
            root = build(Path(tmp), files)
            got = check(root, **kw)
            got_codes = codes(got)
            ok = expect <= got_codes and not (absent & got_codes)
            if name == "good tree passes":
                ok = ok and not codes(got, "error")
            if name.startswith("strict"):
                ok = ok and "C06" in codes(got, "error")
            if not ok:
                failed += 1
                print(f"FAIL {name}: expected {sorted(expect)}, absent {sorted(absent)}, got:")
                for x in got:
                    print(f"  {x}")
            else:
                print(f"ok   {name}")
    print(f"{len(cases) - failed}/{len(cases)} self-test cases passed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="check_docs.py",
        description=__doc__.split("\n\n", 1)[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    ap.add_argument("--docs", default="docs", help="docs folder relative to ROOT (default: docs)")
    ap.add_argument("--require-approved", action="store_true", help="fail unless the inception record is approved")
    ap.add_argument("--changed", metavar="FILE", help="file with changed paths, one per line; '-' for stdin")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--self-test", action="store_true", help="run the built-in fixtures")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    root = Path(args.root)
    if not root.is_dir():
        print(f"{args.root}: not a directory", file=sys.stderr)
        return 2
    changed = None
    if args.changed:
        if args.changed == "-":
            changed = sys.stdin.read().splitlines()
        else:
            try:
                changed = Path(args.changed).read_text(encoding="utf-8").splitlines()
            except OSError as e:
                print(f"{args.changed}: {e}", file=sys.stderr)
                return 2
    findings = check(root, args.docs, args.require_approved, changed, args.strict)
    for x in findings:
        print(x)
    errors = [x for x in findings if x.level == "error"]
    if not findings:
        print("docs check passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
