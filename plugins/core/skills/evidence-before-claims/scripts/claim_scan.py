#!/usr/bin/env python3
"""List status, authorship and security claims in a repository's Markdown, so each one can be checked
against its evidence before a push or before the repository goes public.

Usage:
  claim_scan.py [ROOT] [--files FILE ...]
  claim_scan.py --self-test

ROOT defaults to the current directory. Without --files the scan covers the files where a project
states facts about itself: every *.md at the root of ROOT (README, SECURITY, CHANGELOG, CONTRIBUTING)
and every *.md under docs/; git-tracked files only when ROOT is a git work tree. Pass --files to scan
other files. Fenced code blocks are skipped.

Findings (code, level, what it means):
  C01 error    a status claim (CI or tests green or red, "never ran", "not yet deployed", "is live",
               "production-ready", "fully tested") with no date (YYYY-MM-DD) and no commit hash on
               the same line. Date it with its evidence, or remove it. Badge-only lines are skipped:
               a badge shows the live state.
  C02 error    a security claim with no checkable content ("military-grade", "unbreakable",
               "100% secure", "completely anonymous"). Name what is guaranteed, against which
               attacker, and what is not claimed.
  C03 warning  a named security property ("end-to-end encrypted", "zero-knowledge", "forward
               secrecy", "tamper-proof", "anonymous"). Check that the text states its scope and the
               mechanism, and that the design gives exactly that.
  C04 warning  an authorship or decision claim ("the maintainer decided", "written by hand", "every
               decision was made by"). Check it against the ADR record and git history; it must say
               who proposed and who accepted.

Output: one finding per line as "path:line: level code message". The scanner lists claims; it does
not judge them, so a clean run means no claim of these kinds was found, not that all claims are true.
Exit 0 when there is no error, 1 otherwise, 2 on a usage error. Python 3.8 or later, standard
library only, no network.
"""
from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", ".venv", "dist", "build"}

STATUS_RES = [
    re.compile(r"\b(?:CI|builds?|pipelines?|workflows?|(?:all|the)\s+(?:\d+\s+)?tests|test suite|checks)\b"
               r"[^.\n]{0,40}?\b(?:is|are|was|were|stays?|now|currently)\s+(?:green|red|passing|failing)\b", re.I),
    re.compile(r"\b(?:CI|pipeline|build|all\s+(?:\d+\s+)?(?:tests|checks)|the\s+(?:test\s+)?suite)\s+"
               r"(?:pass|passes|passed|fails|failed)\b", re.I),
    re.compile(r"\bnever\s+(?:been\s+)?(?:run|ran|tested|built|deployed)\b", re.I),
    re.compile(r"\bnot\s+yet\s+(?:been\s+)?(?:run|tested|built|deployed|released|live)\b", re.I),
    re.compile(r"\b(?:is|are)\s+(?:now\s+)?(?:live|deployed|in production)\b", re.I),
    re.compile(r"\bproduction[- ]ready\b|\bbattle[- ]tested\b|\b(?:fully|100\s?%)\s+tested\b", re.I),
]
VAGUE_SECURITY_RE = re.compile(
    r"\b(?:military|bank)[- ]grade\b|\bun(?:breakable|hackable|crackable)\b|\bhacker[- ]proof\b|"
    r"\bbullet[- ]?proof\b|\b(?:100\s?%|fully|completely|totally|perfectly|absolutely)\s+"
    r"(?:secure|safe|anonymous|private|untraceable)\b", re.I)
PROPERTY_RE = re.compile(
    r"\bend[- ]to[- ]end[- ]encrypt\w*|\bzero[- ]knowledge\b|\b(?:perfect\s+)?forward\s+secrecy\b|"
    r"\btamper[- ](?:proof|evident)\b|\banonymous(?:ly)?\b|\bunlinkable\b|\bencrypted\s+at\s+rest\b", re.I)
AUTHORSHIP_RE = re.compile(
    r"\b(?:the\s+)?(?:maintainer|author|owner|team|developer)s?\s+(?:alone\s+|personally\s+|himself\s+|"
    r"herself\s+|themselves\s+)?(?:decided|chose|designed|wrote|made\s+(?:all|every|each))\b|"
    r"\b(?:decided|chosen|designed|written|made|taken)\s+by\s+(?:the\s+)?(?:maintainer|author|owner|team|me|us|hand)\b|"
    r"\b(?:hand[- ]written|hand[- ]crafted|written\s+by\s+hand)\b|"
    r"\bwithout\s+(?:any\s+)?(?:AI|LLM|machine|agent)\s*(?:help|assistance|support)?\b|"
    r"\b(?:all|every|each)\s+(?:\w+\s+){0,2}(?:decision|choice|detail)s?\s+(?:was|were)\s+(?:made|taken|decided|chosen)\b",
    re.I)
DATE_OR_SHA_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b[0-9a-f]{7,40}\b")
BADGE_LINE_RE = re.compile(r"^\s*(?:\[?!\[[^\]]*\]\([^)]*\)\]?(?:\([^)]*\))?\s*)+$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def in_scope(rel: Path) -> bool:
    parts = rel.parts
    if rel.suffix.lower() != ".md" or any(part in SKIP_DIRS for part in parts):
        return False
    return len(parts) == 1 or parts[0] == "docs"


def md_files(root: Path) -> list[Path]:
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout:
            return sorted(root / p for p in r.stdout.split("\0") if p and in_scope(Path(p)))
    except (OSError, subprocess.TimeoutExpired):
        pass
    return sorted(p for p in root.rglob("*.md") if in_scope(p.relative_to(root)))


def scan_text(rel: str, text: str) -> list[tuple[str, int, str, str, str]]:
    found = []
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced or BADGE_LINE_RE.match(line):
            continue
        if any(rx.search(line) for rx in STATUS_RES) and not DATE_OR_SHA_RE.search(line):
            found.append((rel, n, "error", "C01", "status claim without a date or commit; date it with its "
                                                  "evidence (CI run for that commit, deploy record) or remove it"))
        if VAGUE_SECURITY_RE.search(line):
            found.append((rel, n, "error", "C02", "security claim with no checkable content; say what is "
                                                  "guaranteed, against whom, and what is not claimed"))
        elif PROPERTY_RE.search(line):
            found.append((rel, n, "warning", "C03", "named security property; check scope, mechanism and what "
                                                    "is not claimed"))
        if AUTHORSHIP_RE.search(line):
            found.append((rel, n, "warning", "C04", "authorship or decision claim; check it against the ADR "
                                                    "record and git history"))
    return found


def run(root: Path, files: list[Path] | None, out=print) -> int:
    paths = files if files else md_files(root)
    errors = 0
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            rel = str(p.resolve().relative_to(root.resolve()))
        except ValueError:
            rel = str(p)
        for f in scan_text(rel, text):
            out(f"{f[0]}:{f[1]}: {f[2]} {f[3]} {f[4]}")
            errors += f[2] == "error"
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)
    files = None
    if "--files" in args:
        i = args.index("--files")
        files = [Path(a) for a in args[i + 1:]]
        args = args[:i]
        if not files:
            print("--files needs at least one file", file=sys.stderr)
            return 2
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print(__doc__.split("Findings")[0].strip(), file=sys.stderr)
        return 2
    root = Path(args[0]) if args else Path(".")
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    return run(root, files)


def codes(text: str) -> list[str]:
    return [f[3] for f in scan_text("x.md", text)]


def self_test() -> int:
    fails = []

    def check(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    check("undated green claim", codes("CI is green on every push.\n"), ["C01"])
    # lint-allow: L13 sample commit hash for the dated-claim case
    check("dated green claim", codes("CI was green for 0e6465c on 2026-11-04.\n"), [])
    check("never ran", codes("This has never run on GitHub.\n"), ["C01"])
    check("not yet deployed", codes("The API is not yet deployed.\n"), ["C01"])
    check("is live", codes("The site is live.\n"), ["C01"])
    check("production-ready", codes("A production-ready starter.\n"), ["C01"])
    check("tests pass", codes("All tests pass.\n"), ["C01"])
    check("suite was green", codes("The test suite was green before the release.\n"), ["C01"])
    check("generic test prose", codes("Break the guard and see that the test fails.\n"), [])
    check("badge line skipped", codes("[![build is passing](https://example.org/b.svg)](https://example.org/a)\n"), [])
    check("fenced block skipped", codes("```\nCI is green\n```\n"), [])
    check("vague security", codes("Messages use military-grade crypto.\n"), ["C02"])
    check("completely anonymous", codes("Senders stay completely anonymous.\n"), ["C02"])
    check("named property warns", codes("Notes are end-to-end encrypted.\n"), ["C03"])
    check("forward secrecy warns", codes("No claim about forward secrecy is made.\n"), ["C03"])
    check("maintainer decided", codes("The maintainer decided every protocol detail.\n"), ["C04"])
    check("all decisions made", codes("All protocol decisions were made by a human.\n"), ["C04"])
    check("hand-written", codes("The parser is hand-written.\n"), ["C04"])
    check("made by the maintainer", codes("Every protocol decision in it was made by the maintainer alone.\n"), ["C04"])
    check("neutral prose", codes("Run the tests with make test before you open a pull request.\n"), [])
    check("plain decision record", codes("Options and a recommendation are in docs/adr/0003.md.\n"), [])

    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / "docs").mkdir()
        (root / "README.md").write_text("Status: CI is green.\n", encoding="utf-8")
        (root / "docs" / "spec.md").write_text("Data is encrypted at rest.\n", encoding="utf-8")
        (root / "docs" / "node_modules").mkdir()
        (root / "docs" / "node_modules" / "x.md").write_text("CI is green\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "notes.md").write_text("CI is green\n", encoding="utf-8")
        lines: list[str] = []
        check("tree exit on error", run(root, None, lines.append), 1)
        check("tree findings", sorted(l.split(": ")[0] for l in lines), ["README.md:1", "docs/spec.md:1"])
        (root / "README.md").write_text("Status on 2026-11-04: CI is green.\n", encoding="utf-8")
        check("tree exit with warnings only", run(root, None, lambda *_: None), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            check("usage error", main(["--bogus"]), 2)

    if fails:
        for f in fails:
            print("FAIL", f)
        print(f"self-test: {len(fails)} failure(s)")
        return 1
    print("self-test: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
