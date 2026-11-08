#!/usr/bin/env python3
"""Lint an executor spec before hand-off and verify the executor's result after it.

Usage:
  check_handoff.py lint SPEC.md
  check_handoff.py verify SPEC.md [--repo ROOT] [--base REF] [--report REPORT.md]
  check_handoff.py hash FILE...
  check_handoff.py rules
  check_handoff.py --self-test

lint checks that the spec leaves the executor no decision to make. verify checks what the executor
did: protected files unchanged, nothing changed outside the file list, every step reported. hash prints
"path | sha256" rows for the Protected files table. rules prints the fixed Executor rules block that
every spec carries verbatim.

lint (code, level, what fails):
  H01 error    a header field (Spec-ID, Status, Round, Base) or a required section is missing
  H02 error    a step under "## Steps" has no **Change:**, **Check:** or **Expect:** line, or one is empty
  H03 error    vague wording outside code that leaves a choice to the executor ("as needed",
               "appropriate", "suitable", "etc.", "TBD", "if necessary", "you may", "optionally",
               "handle errors", "clean up", "similar to", "and so on", "best practice", "improve")
  H04 error    the Files table has no rows, a row has no path, or an action other than create, modify
               or delete
  H05 error    a Protected files row has no path or a value that is not a 64-character sha256
  H06 error    the Executor rules block is missing or differs from the canonical text (print it with
               "check_handoff.py rules")
  H07 error    a placeholder is left: a template field in square brackets (links and [x] pass),
               a word in angle brackets, TODO, FIXME, XXX, ???
  H08 error    Status is not one of draft, ready, in-progress, review, accepted, changes, needs-human;
               or Round is not k/N with 1 <= k <= N <= 5
  H09 warning  a step names a path in backticks that is in neither the Files nor the Protected table
  H10 warning  more than 6 files or more than 12 steps: split the work into packages
  H11 error    "## Acceptance" has no command in a fenced block

verify (code, level, what fails):
  V01 error    a protected file is missing or its sha256 differs from the table
  V02 error    a file changed since Base (tracked or untracked) that is not in the Files table and not
               under the spec's own directory
  V03 error    the report is missing, or lacks one of the sections Steps, Deviations, Questions
  V04 error    a step id from the spec does not appear in the report's Steps section
  V05 warning  the report has open questions: answer them in the spec before the next round
  V06 warning  Deviations is not "none"
  V07 error    a file listed with action delete still exists, or one listed with create does not

Output: one finding per line as "path:line: level code message". Exit 0 when there is no error,
1 otherwise, 2 on a usage error or a missing file. verify needs git. Python 3.8 or later, standard
library only.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXECUTOR_RULES = """\
You are the executor of this spec. Every design decision is already made in it.
1. Do the steps in order. After each step run its Check and compare the output with its Expect. Start
   the next step only when they match.
2. Change only the files in the Files table. Never edit a file in the Protected files table. Never add,
   remove or upgrade a dependency, and never touch configuration, CI or lock files unless the Files
   table lists them.
3. Use only names (files, functions, classes, routes, flags, keys, packages) that appear in this spec or
   that a search in the repository showed you. Never invent an API.
4. Do not redesign, rename, refactor, reformat or improve anything the steps do not ask for, even when
   you think it is better.
5. Stop and ask when: the text a step says to find is not there exactly; a Check fails twice and the
   second output told you nothing new; you need a file, name, value or dependency the spec does not
   give; a step can be read two ways; a protected test fails for a reason you cannot explain. Write
   the question under Questions in the report as: Step, What is missing, What I checked, Options I
   see, What I would do. Then continue only with steps that do not depend on the answer. Never guess
   to keep going; a precise question is a good result.
6. Never make a failure disappear: no skipped or deleted test, no ignore comment, no catch-all, no
   "|| true", no looser type, no disabled check.
7. Never push, deploy, publish, send messages, run migrations against a shared database, or read
   secrets. Work only in the checkout you were given.
8. Write the report in the format of the Report section: each step as done, blocked or not started,
   with the Check command and the last lines of its output. A step is done only when its Expect
   matched. List every deviation from the spec, or write "none".
"""

HEADER_FIELDS = ("Spec-ID", "Status", "Round", "Base")
SECTIONS = ("Goal", "Scope", "Out of scope", "Files", "Protected files", "Context", "Steps",
            "Acceptance", "Stop and ask", "Report", "Executor rules")
STATUSES = {"draft", "ready", "in-progress", "review", "accepted", "changes", "needs-human"}
ACTIONS = {"create", "modify", "delete"}
REPORT_SECTIONS = ("Steps", "Deviations", "Questions")
VAGUE_RE = re.compile(
    r"(?<![\w-])(?:as needed|as appropriate|appropriate(?:ly)?|suitable|etc\.?|tbd|if necessary|"
    r"if needed|where needed|you may|optionally|handle (?:the )?errors?(?: properly| gracefully)?|"
    r"clean ?up|similar to|and so on|best practices?|improve|make sure it works|"
    r"whatever|somehow|some kind of|reasonable|sensible)(?![\w-])",
    re.I,
)
PLACEHOLDER_RE = re.compile(r"<[a-z][\w -]*>|\bTODO\b|\bFIXME\b|\bXXX\b|\?\?\?|\[(?![ xX]\])[^\]\n]{2,}\](?!\()")
TICK_PLACEHOLDER_RE = re.compile(r"`\[[^\]`]+\]`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BACKTICK_RE = re.compile(r"`[^`]*`")
PATH_TICK_RE = re.compile(r"`((?:\.{0,2}/)?(?:[\w.@-]+/)+[\w.@-]+\.[A-Za-z0-9]{1,8}|[\w.@-]+\.[A-Za-z]{1,8})`")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
STEP_RE = re.compile(r"^###\s+(S\d+)\b")
ROUND_RE = re.compile(r"^(\d+)\s*/\s*(\d+)$")
RULES_BEGIN = "<!-- executor-rules:begin -->"
RULES_END = "<!-- executor-rules:end -->"


def norm(text: str) -> str:
    return " ".join(text.split())


class Spec:
    def __init__(self, path: Path):
        self.path = path
        self.lines = path.read_text(encoding="utf-8").splitlines()
        self.header: dict[str, tuple[str, int]] = {}
        self.sections: dict[str, int] = {}
        self.code = [False] * len(self.lines)
        in_code = False
        for i, line in enumerate(self.lines):
            if FENCE_RE.match(line):
                self.code[i] = True
                in_code = not in_code
                continue
            self.code[i] = in_code
            if in_code:
                continue
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m and not line.startswith("###"):
                self.sections.setdefault(m.group(1).strip().lower(), i)
            if not self.sections:
                m = re.match(r"^\s*[-*]?\s*\**([A-Za-z-]+)\**\s*:\s*(.*)$", line)
                if m and m.group(1) in HEADER_FIELDS:
                    self.header.setdefault(m.group(1), (m.group(2).strip(), i + 1))

    def section(self, name: str) -> list[tuple[int, str]]:
        start = self.sections.get(name.lower())
        if start is None:
            return []
        out = []
        for i in range(start + 1, len(self.lines)):
            if not self.code[i] and re.match(r"^##\s", self.lines[i]) and not self.lines[i].startswith("###"):
                break
            out.append((i + 1, self.lines[i]))
        return out

    def table(self, name: str) -> list[tuple[int, list[str]]]:
        rows = []
        for n, line in self.section(name):
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            rows.append((n, cells))
        return rows[1:] if rows else []  # drop the column header row

    def files(self) -> list[tuple[int, str, str]]:
        return [(n, c[0].strip("`"), (c[1].lower() if len(c) > 1 else "")) for n, c in self.table("Files")]

    def protected(self) -> list[tuple[int, str, str]]:
        return [(n, c[0].strip("`"), (c[1].strip("`").lower() if len(c) > 1 else "")) for n, c in self.table("Protected files")]

    def steps(self) -> list[tuple[str, int, list[tuple[int, str]]]]:
        out = []
        cur = None
        for n, line in self.section("Steps"):
            m = STEP_RE.match(line)
            if m:
                cur = (m.group(1), n, [])
                out.append(cur)
            elif cur is not None:
                cur[2].append((n, line))
        return out


def rules_block(lines: list[str]) -> str | None:
    text = "\n".join(lines)
    a, b = text.find(RULES_BEGIN), text.find(RULES_END)
    if a < 0 or b < a:
        return None
    return text[a + len(RULES_BEGIN):b]


def lint(path: Path) -> list[tuple[int, str, str, str]]:
    spec = Spec(path)
    f: list[tuple[int, str, str, str]] = []
    for key in HEADER_FIELDS:
        if key not in spec.header or not spec.header[key][0]:
            f.append((1, "error", "H01", f"header field '{key}:' is missing or empty"))
    for name in SECTIONS:
        if name.lower() not in spec.sections:
            f.append((1, "error", "H01", f"section '## {name}' is missing"))
    if "Status" in spec.header:
        val, n = spec.header["Status"]
        if val and val.lower() not in STATUSES:
            f.append((n, "error", "H08", f"Status '{val}' is not one of {', '.join(sorted(STATUSES))}"))
    if "Round" in spec.header:
        val, n = spec.header["Round"]
        m = ROUND_RE.match(val)
        if val and (not m or not (1 <= int(m.group(1)) <= int(m.group(2)) <= 5)):
            f.append((n, "error", "H08", f"Round '{val}' must be k/N with 1 <= k <= N <= 5"))

    files = spec.files()
    if "files" in spec.sections and not files:
        f.append((spec.sections["files"] + 1, "error", "H04", "the Files table has no rows"))
    for n, p, action in files:
        if not p:
            f.append((n, "error", "H04", "Files row without a path"))
        if action not in ACTIONS:
            f.append((n, "error", "H04", f"action '{action}' must be create, modify or delete"))
    for n, p, sha in spec.protected():
        if not p:
            f.append((n, "error", "H05", "Protected files row without a path"))
        if p and p.lower() not in {"none"} and not SHA_RE.match(sha):
            f.append((n, "error", "H05", f"'{p}' has no 64-character sha256 (use: check_handoff.py hash {p})"))

    block = rules_block(spec.lines)
    if block is None:
        f.append((1, "error", "H06", f"Executor rules block between {RULES_BEGIN} and {RULES_END} is missing"))
    elif norm(block.replace("```", "")) != norm(EXECUTOR_RULES):
        f.append((1, "error", "H06", "Executor rules block differs from the canonical text; replace it with 'check_handoff.py rules'"))

    in_rules = False
    for i, line in enumerate(spec.lines):
        if RULES_BEGIN in line:
            in_rules = True
        if RULES_END in line:
            in_rules = False
            continue
        if in_rules or spec.code[i]:
            continue
        bare = BACKTICK_RE.sub("", line)
        if line.lstrip().startswith("<!--"):
            continue
        m = VAGUE_RE.search(bare)
        if m:
            f.append((i + 1, "error", "H03", f"vague wording '{m.group(0)}' leaves a choice to the executor; say exactly what to do"))
        m = PLACEHOLDER_RE.search(bare) or TICK_PLACEHOLDER_RE.search(line)
        if m:
            f.append((i + 1, "error", "H07", f"placeholder '{m.group(0)}' left in the spec"))

    known = {p for _, p, _ in files} | {p for _, p, _ in spec.protected()}
    steps = spec.steps()
    if "steps" in spec.sections and not steps:
        f.append((spec.sections["steps"] + 1, "error", "H02", "no steps; use headings '### S1 ...'"))
    for sid, n, body in steps:
        fields = {}
        for bn, line in body:
            m = re.match(r"^\s*[-*]?\s*\*\*(Change|Check|Expect):\*\*\s*(.*)$", line)
            if m:
                fields[m.group(1)] = (bn, m.group(2).strip())
        for key in ("Change", "Check", "Expect"):
            if key not in fields:
                f.append((n, "error", "H02", f"step {sid} has no **{key}:** line"))
            elif not fields[key][1]:
                # an empty inline value is fine when a fenced block follows directly
                bn = fields[key][0]
                nxt = next((l for k, l in body if k > bn and l.strip()), "")
                if not FENCE_RE.match(nxt):
                    f.append((bn, "error", "H02", f"step {sid} has an empty **{key}:**"))
        for bn, line in body:
            if spec.code[bn - 1]:
                continue
            for m in PATH_TICK_RE.finditer(line):
                cand = m.group(1)
                if "/" in cand and cand not in known:
                    f.append((bn, "warning", "H09", f"step {sid} names `{cand}`, which is in neither Files nor Protected files"))
    if len(files) > 6 or len(steps) > 12:
        f.append((1, "warning", "H10", f"{len(files)} files and {len(steps)} steps; split into packages of at most 6 files and 12 steps"))

    acc = spec.section("Acceptance")
    if "acceptance" in spec.sections and not any(spec.code[n - 1] and not FENCE_RE.match(l) and l.strip() for n, l in acc):
        f.append((spec.sections["acceptance"] + 1, "error", "H11", "Acceptance has no command in a fenced block"))
    return f


def git(repo: Path, *args: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return [l for l in out.stdout.splitlines() if l.strip()]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(spec_path: Path, repo: Path, base: str | None, report: Path | None) -> list[tuple[str, int, str, str, str]]:
    spec = Spec(spec_path)
    f: list[tuple[str, int, str, str, str]] = []
    sp = str(spec_path)
    for n, p, sha in spec.protected():
        if not p or p.lower() == "none":
            continue
        target = repo / p
        if not target.is_file():
            f.append((sp, n, "error", "V01", f"protected file '{p}' is missing"))
        elif SHA_RE.match(sha) and sha256(target) != sha:
            f.append((sp, n, "error", "V01", f"protected file '{p}' was changed (sha256 differs)"))
    base = base or spec.header.get("Base", ("", 0))[0]
    if not base:
        f.append((sp, 1, "error", "V02", "no Base in the header and no --base given"))
    else:
        changed = set(git(repo, "diff", "--name-only", base)) | set(git(repo, "ls-files", "--others", "--exclude-standard"))
        allowed = {p for _, p, _ in spec.files()}
        protected = {p for _, p, _ in spec.protected()}  # V01 reports these
        try:
            spec_dir = spec_path.resolve().parent.relative_to(repo.resolve()).as_posix()
        except ValueError:
            spec_dir = None
        for c in sorted(changed):
            if c in allowed or c in protected or (spec_dir and (c == spec_dir or c.startswith(spec_dir + "/"))):
                continue
            f.append((sp, 1, "error", "V02", f"'{c}' changed but is not in the Files table"))
    for n, p, action in spec.files():
        exists = (repo / p).exists()
        if action == "delete" and exists:
            f.append((sp, n, "error", "V07", f"'{p}' should be deleted but still exists"))
        if action == "create" and not exists:
            f.append((sp, n, "error", "V07", f"'{p}' should be created but does not exist"))

    report = report or spec_path.parent / "REPORT.md"
    rp = str(report)
    if not report.is_file():
        f.append((rp, 0, "error", "V03", "report is missing"))
        return f
    rep = Spec(report)
    for name in REPORT_SECTIONS:
        if name.lower() not in rep.sections:
            f.append((rp, 1, "error", "V03", f"report has no '## {name}' section"))
    steps_text = "\n".join(l for _, l in rep.section("Steps"))
    for sid, n, _ in spec.steps():
        if not re.search(rf"\b{sid}\b", steps_text):
            f.append((rp, 1, "error", "V04", f"step {sid} is not in the report"))
    q = [l for _, l in rep.section("Questions") if l.strip() and not l.strip().startswith("<!--")]
    if q and norm(" ".join(q)).lower() not in {"none", "none.", "- none"}:
        f.append((rp, 1, "warning", "V05", "the report has open questions; answer them in the spec before the next round"))
    d = [l for _, l in rep.section("Deviations") if l.strip() and not l.strip().startswith("<!--")]
    if not d or norm(" ".join(d)).lower() not in {"none", "none.", "- none"}:
        f.append((rp, 1, "warning", "V06", "Deviations is not 'none'; review each one"))
    return f


def emit(path: str, findings) -> int:
    errors = 0
    for item in findings:
        if len(item) == 4:
            n, level, code, msg = item
            p = path
        else:
            p, n, level, code, msg = item
        print(f"{p}:{n}: {level} {code} {msg}")
        errors += level == "error"
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "rules":
        sys.stdout.write(EXECUTOR_RULES)
        return 0
    if cmd == "hash":
        if not rest:
            print("hash needs at least one file", file=sys.stderr)
            return 2
        for p in rest:
            if not Path(p).is_file():
                print(f"{p}: no such file", file=sys.stderr)
                return 2
            print(f"| `{p}` | {sha256(Path(p))} |")
        return 0
    if cmd in {"lint", "verify"}:
        if not rest or not Path(rest[0]).is_file():
            print(f"{cmd} needs an existing SPEC.md", file=sys.stderr)
            return 2
        spec = Path(rest[0])
        if cmd == "lint":
            return emit(str(spec), lint(spec))
        opts = {"--repo": ".", "--base": None, "--report": None}
        i = 1
        while i < len(rest):
            if rest[i] in opts and i + 1 < len(rest):
                opts[rest[i]] = rest[i + 1]
                i += 2
            else:
                print(f"unknown argument {rest[i]}", file=sys.stderr)
                return 2
        try:
            found = verify(spec, Path(opts["--repo"]), opts["--base"], Path(opts["--report"]) if opts["--report"] else None)
        except (RuntimeError, FileNotFoundError) as e:
            print(f"verify failed: {e}", file=sys.stderr)
            return 2
        return emit(str(spec), found)
    print(f"unknown command {cmd}", file=sys.stderr)
    return 2


GOOD_SPEC = """# Spec: Add a CSV export of invoices

- Spec-ID: invoice-csv-export
- Status: ready
- Round: 1/3
- Base: HEAD

## Goal

Owners download their invoices as CSV so their accountant can import them.

## Scope

One route that streams a CSV of the current tenant's invoices.

## Out of scope

Filtering, other formats, background jobs.

## Files

| Path | Action | Purpose |
|---|---|---|
| `src/export.py` | create | the export function |
| `src/routes.py` | modify | register the route |

## Protected files

| Path | sha256 |
|---|---|
| `tests/test_export.py` | {sha} |

## Context

Current end of `src/routes.py`:

```python
ROUTES = {{}}
```

## Steps

### S1 Create the export function

**Change:** create `src/export.py` with exactly this content:

```python
def export(rows):
    return "\\n".join(",".join(r) for r in rows)
```

**Check:** `python3 -c "import src.export"`
**Expect:** exit code 0, no output

### S2 Register the route

**Change:** in `src/routes.py` replace `ROUTES = {{}}` with `ROUTES = {{"/invoices.csv": "export"}}`.
**Check:** `grep -c invoices.csv src/routes.py`
**Expect:** `1`

## Acceptance

```sh
python3 -m pytest tests/test_export.py -q
```

Expect: 2 passed.

## Stop and ask

Stop if `ROUTES = {{}}` is not in `src/routes.py` exactly once.

## Report

Write `REPORT.md` next to this spec with the sections Steps, Checks, Deviations, Questions.

## Executor rules

{begin}
{rules}{end}
"""


def self_test() -> int:
    ok = True

    def expect(label: str, codes: list[str], findings) -> None:
        nonlocal ok
        got = sorted({x[-2] for x in findings if x[-3] == "error" or x[-2] in codes})
        want = sorted(set(codes))
        if got != want:
            ok = False
            print(f"FAIL {label}: want {want}, got {got}")
            for x in findings:
                print("   ", x)

    tmp = Path(tempfile.mkdtemp())
    try:
        repo = tmp / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "src" / "routes.py").write_text("ROUTES = {}\n")
        (repo / "tests" / "test_export.py").write_text("def test_a(): pass\ndef test_b(): pass\n")
        sha = sha256(repo / "tests" / "test_export.py")
        spec_dir = repo / "docs" / "handoff" / "invoice-csv-export"
        spec_dir.mkdir(parents=True)
        good = GOOD_SPEC.format(sha=sha, begin=RULES_BEGIN, end=RULES_END, rules=EXECUTOR_RULES)
        spec = spec_dir / "SPEC.md"

        def lint_text(text: str):
            spec.write_text(text)
            return lint(spec)

        expect("good spec", [], lint_text(good))
        expect("vague word", ["H03"], lint_text(good.replace("Filtering, other formats", "Filtering etc.")))
        expect("vague in backticks passes", [], lint_text(good.replace("Filtering, other", "Filtering, `as needed`, other")))
        expect("placeholder", ["H07"], lint_text(good.replace("Owners download", "TODO Owners download")))
        expect("template field left", ["H07"], lint_text(good.replace("One route that", "[what this package delivers] One route that")))
        expect("template path left", ["H07"], lint_text(good.replace("`src/export.py` | create", "`[path]` | create")))
        expect("link passes", [], lint_text(good.replace("their accountant", "their [accountant](https://example.com)")))
        expect("missing Check", ["H02"], lint_text(good.replace('**Check:** `grep -c invoices.csv src/routes.py`\n', "")))
        expect("missing section", ["H01"], lint_text(good.replace("## Stop and ask", "## Notes")))
        expect("missing header", ["H01"], lint_text(good.replace("- Base: HEAD\n", "")))
        expect("bad status", ["H08"], lint_text(good.replace("Status: ready", "Status: wip")))
        expect("bad round", ["H08"], lint_text(good.replace("Round: 1/3", "Round: 4/3")))
        expect("bad action", ["H04"], lint_text(good.replace("| modify |", "| edit |")))
        expect("bad sha", ["H05"], lint_text(good.replace(sha, sha[:40])))
        expect("altered rules", ["H06"], lint_text(good.replace("Never invent an API.", "Invent APIs when useful.")))
        expect("missing rules", ["H03", "H06"], lint_text(good.replace(RULES_BEGIN, "")))
        expect("no acceptance command", ["H11"], lint_text(good.replace("python3 -m pytest tests/test_export.py -q\n", "")))
        expect("unknown path warns", ["H09"], lint_text(good.replace("in `src/routes.py` replace", "in `src/other.py` replace")))

        template = Path(__file__).resolve().parent.parent / "references" / "spec-template.md"
        if template.is_file():
            block = rules_block(template.read_text(encoding="utf-8").splitlines())
            if block is None or norm(block.replace("```", "")) != norm(EXECUTOR_RULES):
                ok = False
                print("FAIL template: references/spec-template.md rules block differs from EXECUTOR_RULES")

        if shutil.which("git"):
            spec.write_text(good)
            g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run(g[:3] + ["init", "-q"], check=True)
            subprocess.run(g + ["add", "-A"], check=True)
            subprocess.run(g + ["commit", "-qm", "base"], check=True)
            report = spec_dir / "REPORT.md"
            good_report = "# Report\n\n## Steps\n\n- S1 done\n- S2 done\n\n## Checks\n\nok\n\n## Deviations\n\nnone\n\n## Questions\n\nnone\n"

            def run_verify():
                return verify(spec, repo, None, None)

            report.write_text(good_report)
            expect("verify: nothing done", ["V07"], run_verify())
            (repo / "src" / "export.py").write_text("def export(rows): pass\n")
            (repo / "src" / "routes.py").write_text('ROUTES = {"/invoices.csv": "export"}\n')
            expect("verify: good", [], run_verify())
            (repo / "src" / "helpers.py").write_text("x = 1\n")
            expect("verify: file outside list", ["V02"], run_verify())
            (repo / "src" / "helpers.py").unlink()
            (repo / "tests" / "test_export.py").write_text("def test_a(): pass\n")
            expect("verify: protected changed", ["V01"], run_verify())
            (repo / "tests" / "test_export.py").write_text("def test_a(): pass\ndef test_b(): pass\n")
            report.write_text(good_report.replace("- S2 done\n", ""))
            expect("verify: step missing", ["V04"], run_verify())
            report.write_text(good_report.replace("## Questions\n\nnone", "## Questions\n\nS2: which route name?"))
            expect("verify: open question", ["V05"], run_verify())
            report.write_text(good_report.replace("## Deviations\n\nnone", "## Deviations\n\nrenamed export"))
            expect("verify: deviation", ["V06"], run_verify())
            report.unlink()
            expect("verify: no report", ["V03"], run_verify())
        else:
            print("note: git not found, verify cases skipped")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("self-test passed" if ok else "self-test FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
