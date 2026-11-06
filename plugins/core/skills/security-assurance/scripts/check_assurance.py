#!/usr/bin/env python3
"""Check the security assurance table in docs/SECURITY-ASSURANCE.md.

Usage:
  check_assurance.py [ROOT] [--file FILE]
  check_assurance.py --self-test

ROOT defaults to the current directory. FILE defaults to docs/SECURITY-ASSURANCE.md under ROOT;
evidence paths are resolved against ROOT.

The table sits under a heading "## Security assurance" with the columns Property | Asset |
Attacker | Mechanism | Evidence | Not covered (more columns are allowed). One row per property.

Checks (code, level, what fails):
  A01 error    no "## Security assurance" heading, no table under it, a missing column, or no rows
  A02 error    a required cell is empty
  A03 error    a vague label instead of a property in Property, Mechanism or Evidence
               ("secure", "fully encrypted", "military-grade", "bank-level", "unbreakable",
               "100%" ...); text in backticks is ignored, so `Secure` as a cookie flag passes
  A04 error    Not covered says nothing ("none", "n/a", "-", "nothing")
  A05 error    Evidence names neither an existing file nor an https:// link
  A06 error    Evidence names a file that does not exist
  A07 warning  Evidence has no test file (no path with "test" or "spec" in it), only documents

Output: one finding per line as "path:line: level code message". Exit 0 when there is no error,
1 otherwise, 2 on a usage error or a missing file. Python 3.8 or later, standard library only.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

REQUIRED = ("property", "asset", "attacker", "mechanism", "evidence", "not covered")
VAGUE_RE = re.compile(
    r"(?<![\w-])(?:fully |completely |absolutely |totally )?"
    r"(?:secure|encrypted end to end and secure|military[- ]grade|bank[- ]level|bank[- ]grade|"
    r"enterprise[- ]grade|unbreakable|hack[- ]?proof|bullet[- ]?proof|uncrackable|"
    r"100 ?%(?: secure| safe)?|state[- ]of[- ]the[- ]art security)(?![\w-])",
    re.I,
)
FULLY_RE = re.compile(r"(?<![\w-])(?:fully|completely|absolutely|totally) (?:encrypted|protected|safe)(?![\w-])", re.I)
EMPTY_NOT_COVERED = {"", "none", "n/a", "na", "-", "--", "nothing", "no", "nil", "n.a.", "keine", "nichts"}
URL_RE = re.compile(r"https://\S+")
PATH_RE = re.compile(r"(?<![\w/.-])((?:\.{0,2}/)?(?:[\w.-]+/)*[\w.-]+\.[A-Za-z0-9]{1,8})(?:(?:::|:|#)[\w\\-]+)?")
BACKTICK_RE = re.compile(r"`[^`]*`")
FILE_EXTS = {"php", "py", "js", "mjs", "ts", "tsx", "vue", "go", "rb", "rs", "java", "kt", "cs", "sh", "md", "yml",
             "yaml", "json", "toml", "txt", "pdf", "feature", "sql"}


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def find_table(lines: list[str]):
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+security assurance\s*$", line.strip(), re.I):
            start = i
            break
    if start is None:
        return None, None, []
    header_at = None
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if s.startswith("#"):
            break
        if s.startswith("|"):
            header_at = j
            break
    if header_at is None:
        return start, None, []
    rows = []
    for k in range(header_at + 2, len(lines)):
        s = lines[k].strip()
        if not s.startswith("|"):
            break
        rows.append((k + 1, split_row(s)))
    return start, (header_at + 1, [c.lower() for c in split_row(lines[header_at])]), rows


def evidence_paths(text: str) -> list[str]:
    out = []
    for m in PATH_RE.finditer(URL_RE.sub(" ", text)):
        p = m.group(1)
        if "/" in p or p.rsplit(".", 1)[-1].lower() in FILE_EXTS:
            out.append(p)
    return out


def check(root: Path, file: Path) -> list[tuple[int, str, str, str]]:
    findings: list[tuple[int, str, str, str]] = []
    lines = file.read_text(encoding="utf-8").splitlines()
    start, header, rows = find_table(lines)
    if start is None:
        return [(1, "error", "A01", 'no "## Security assurance" heading')]
    if header is None:
        return [(start + 1, "error", "A01", "no table under the heading")]
    hline, cols = header
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        return [(hline, "error", "A01", "missing column(s): " + ", ".join(missing))]
    if not rows:
        return [(hline, "error", "A01", "the table has no rows")]
    idx = {c: cols.index(c) for c in REQUIRED}
    for n, cells in rows:
        cells = cells + [""] * (len(cols) - len(cells))
        cell = {c: cells[idx[c]] for c in REQUIRED}
        for c in REQUIRED:
            if c != "not covered" and not cell[c]:
                findings.append((n, "error", "A02", f"empty cell: {c}"))
        for c in ("property", "mechanism", "evidence"):
            bare = BACKTICK_RE.sub(" ", cell[c])
            m = VAGUE_RE.search(bare) or FULLY_RE.search(bare)
            if m:
                findings.append((n, "error", "A03", f"vague label in {c}: '{m.group(0)}'; name the property"))
        if cell["not covered"].strip().strip(".").lower() in EMPTY_NOT_COVERED:
            findings.append((n, "error", "A04", "not covered is empty; name the attacker this does not stop"))
        ev = cell["evidence"]
        if not ev:
            continue
        paths = evidence_paths(BACKTICK_RE.sub(lambda m: " " + m.group(0)[1:-1] + " ", ev))
        existing = [p for p in paths if (root / p).is_file()]
        for p in paths:
            if not (root / p).is_file():
                findings.append((n, "error", "A06", f"evidence file does not exist: {p}"))
        if not existing and not URL_RE.search(ev):
            findings.append((n, "error", "A05", "evidence names no existing file and no https:// link"))
        elif not any(re.search(r"test|spec", p, re.I) for p in existing):
            findings.append((n, "warning", "A07", "evidence has no test file; an attack test is the proof"))
    return findings


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)
    file_arg = None
    if "--file" in args:
        i = args.index("--file")
        if i + 1 >= len(args):
            print("--file needs a value", file=sys.stderr)
            return 2
        file_arg = args[i + 1]
        del args[i:i + 2]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print(__doc__.split("Checks")[0].strip(), file=sys.stderr)
        return 2
    root = Path(args[0] if args else ".").resolve()
    file = Path(file_arg) if file_arg else root / "docs" / "SECURITY-ASSURANCE.md"
    if not file.is_absolute() and file_arg:
        file = (Path.cwd() / file).resolve()
    if not file.is_file():
        print(f"{file}: no such file; write the table first (see SKILL.md)", file=sys.stderr)
        return 2
    try:
        rel = file.relative_to(root)
    except ValueError:
        rel = file
    findings = check(root, file)
    for n, level, code, msg in findings:
        print(f"{rel}:{n}: {level} {code} {msg}")
    return 1 if any(f[1] == "error" for f in findings) else 0


HEADER = "| Property | Asset | Attacker | Mechanism | Evidence | Not covered |\n|---|---|---|---|---|---|\n"
GOOD_ROW = ("| A download link cannot be changed or reused after expiry | invoice PDFs | holder of an old or edited "
            "link | HMAC-SHA-256 over path, query and expiry; constant-time compare | "
            "`tests/SignedDownloadTest.php::tamper` | a holder of a valid link before expiry |\n")


def self_test() -> int:
    fails: list[str] = []

    def run(body: str, files=("tests/SignedDownloadTest.php",)) -> list[str]:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for f in files:
                (root / f).parent.mkdir(parents=True, exist_ok=True)
                (root / f).write_text("x", encoding="utf-8")
            (root / "docs").mkdir(exist_ok=True)
            doc = root / "docs" / "SECURITY-ASSURANCE.md"
            doc.write_text(body, encoding="utf-8")
            return sorted({f"{lvl}:{code}" for _, lvl, code, _ in check(root, doc)})

    def expect(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got}, want {want}")

    base = "# Security\n\n## Security assurance\n\n"
    expect("good table", run(base + HEADER + GOOD_ROW), [])
    expect("no heading", run("# Security\n\n" + HEADER + GOOD_ROW), ["error:A01"])
    expect("heading without table", run(base + "Nothing yet.\n\n## Next\n" + HEADER + GOOD_ROW), ["error:A01"])
    expect("missing column", run(base + "| Property | Asset | Attacker | Mechanism | Evidence |\n|---|---|---|---|---|\n"
                                 "| a | b | c | d | `tests/SignedDownloadTest.php` |\n"), ["error:A01"])
    expect("no rows", run(base + HEADER), ["error:A01"])
    expect("empty attacker", run(base + HEADER + GOOD_ROW.replace("holder of an old or edited link", "")),
           ["error:A02"])
    expect("vague property", run(base + HEADER + GOOD_ROW.replace(
        "A download link cannot be changed or reused after expiry", "Downloads are fully secure")), ["error:A03"])
    expect("military-grade mechanism", run(base + HEADER + GOOD_ROW.replace(
        "HMAC-SHA-256 over path, query and expiry; constant-time compare", "military-grade encryption")),
        ["error:A03"])
    expect("fully encrypted", run(base + HEADER + GOOD_ROW.replace(
        "A download link cannot be changed or reused after expiry", "Files are fully encrypted")), ["error:A03"])
    expect("backticked Secure flag passes", run(base + HEADER + GOOD_ROW.replace(
        "HMAC-SHA-256 over path, query and expiry; constant-time compare",
        "session cookie with `Secure` and `HttpOnly`")), [])
    expect("not covered none", run(base + HEADER + GOOD_ROW.replace("a holder of a valid link before expiry", "none")),
           ["error:A04"])
    expect("not covered empty", run(base + HEADER + GOOD_ROW.replace("a holder of a valid link before expiry", "")),
           ["error:A04"])
    expect("evidence without file or link", run(base + HEADER + GOOD_ROW.replace(
        "`tests/SignedDownloadTest.php::tamper`", "we reviewed it")), ["error:A05"])
    expect("evidence file missing", run(base + HEADER + GOOD_ROW, files=()), ["error:A05", "error:A06"])
    expect("link only warns", run(base + HEADER + GOOD_ROW.replace(
        "`tests/SignedDownloadTest.php::tamper`", "https://example.org/audit-2026.pdf")), ["warning:A07"])
    expect("doc file only warns", run(base + HEADER + GOOD_ROW.replace(
        "`tests/SignedDownloadTest.php::tamper`", "`docs/adr/0003-signing.md`"),
        files=("docs/adr/0003-signing.md",)), ["warning:A07"])
    expect("version numbers are not paths", run(base + HEADER + GOOD_ROW.replace(
        "`tests/SignedDownloadTest.php::tamper`", "`tests/SignedDownloadTest.php` with library 2.4.1")), [])
    expect("prose abbreviations are not paths", run(base + HEADER + GOOD_ROW.replace(
        "`tests/SignedDownloadTest.php::tamper`", "`tests/SignedDownloadTest.php`, e.g. the tamper case")), [])
    expect("extra column allowed", run(base + HEADER.replace("| Not covered |", "| Not covered | Owner |")
                                       .replace("|---|---|---|---|---|---|", "|---|---|---|---|---|---|---|")
                                       + GOOD_ROW.rstrip("\n") + " team |\n"), [])

    if fails:
        for f in fails:
            print("FAIL", f)
        print(f"self-test: {len(fails)} failure(s)")
        return 1
    print("self-test: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
