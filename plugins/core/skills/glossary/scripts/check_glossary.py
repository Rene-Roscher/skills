#!/usr/bin/env python3
"""Check glossary tables: the reference files of the glossary skill and a project docs/GLOSSARY.md.

Usage:
  check_glossary.py [PATH ...]
  check_glossary.py --self-test

PATH is a Markdown file or a directory (searched for *.md). Without a PATH the references
directory next to this script is checked. Only tables whose header starts with
`term | aliases` are validated; other tables are ignored.

Two table shapes are accepted:
  reference: term | aliases | what it is | not to confuse with | official URL
  project:   term | aliases | meaning in this project | not to confuse with | source

Checks (code, level, what fails):
  G01 error    a table row does not have exactly five cells
  G02 error    the header of a `term | aliases` table has other column names than the two shapes above
  G03 error    empty term, or an empty or placeholder meaning ("-", TBD, TODO)
  G04 error    an empty "not to confuse with" or source cell (write "-" if there is none)
  G05 error    a URL that is not https:// (reference files: the URL column is https:// or "-")
  G06 error    a duplicate term or alias inside the checked reference files, or inside one project file
  G07 error    a reference file has no "verified YYYY-MM-DD" line in its first 8 lines
  G08 warning  a project term or alias that also appears in a reference file (the project entry wins)

Exit 0 when there is no error, 1 with errors, 2 on a usage error. Python 3.8 or later, standard
library only, no network access. It checks the table format, not whether an entry is true.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

REF_HEAD = ["term", "aliases", "what it is", "not to confuse with", "official url"]
PRJ_HEAD = ["term", "aliases", "meaning in this project", "not to confuse with", "source"]
PLACEHOLDERS = {"", "-", "tbd", "todo", "?", "n/a"}
VERIFIED_RE = re.compile(r"verified\s+\d{4}-\d{2}-\d{2}", re.I)
SKIP_ALIAS_RE = re.compile(r"\s*\((?:old|old name|old name, same company)\)\s*$", re.I)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_sep(line):
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line))


def norm(s):
    s = SKIP_ALIAS_RE.sub("", s.strip())
    s = re.sub(r"^formerly\s+", "", s, flags=re.I)
    return re.sub(r"\s+", " ", s).casefold()


def parse(path):
    """Return (kind, entries, findings). Entry: (line, term, [aliases])."""
    findings, entries, kinds = [], [], set()
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    kind = None
    for i, line in enumerate(lines):
        n = i + 1
        if not line.lstrip().startswith("|"):
            kind = None if line.strip() == "" and kind is None else kind
            if line.strip() == "":
                kind = None
            continue
        if is_sep(line):
            continue
        c = cells(line)
        low = [x.casefold() for x in c]
        if kind is None:
            if low[:2] == ["term", "aliases"]:
                if low == REF_HEAD:
                    kind = "ref"
                elif low == PRJ_HEAD:
                    kind = "prj"
                else:
                    findings.append((path, n, "error", "G02", "header must be '%s' or '%s'" % (" | ".join(REF_HEAD), " | ".join(PRJ_HEAD))))
                    kind = "bad"
                if kind in ("ref", "prj"):
                    kinds.add(kind)
            else:
                kind = "other"
            continue
        if kind in ("other", "bad"):
            continue
        if len(c) != 5:
            findings.append((path, n, "error", "G01", "row has %d cells, expected 5" % len(c)))
            continue
        term, aliases, meaning, confuse, src = c
        if not term:
            findings.append((path, n, "error", "G03", "empty term"))
            continue
        if meaning.casefold() in PLACEHOLDERS:
            findings.append((path, n, "error", "G03", "empty or placeholder meaning for '%s'" % term))
        if not confuse:
            findings.append((path, n, "error", "G04", "empty 'not to confuse with' for '%s' (use -)" % term))
        if not src:
            findings.append((path, n, "error", "G04", "empty source for '%s' (use -)" % term))
        for m in re.finditer(r"http://\S+", " ".join(c)):
            findings.append((path, n, "error", "G05", "non-https URL %s" % m.group(0)))
        if kind == "ref" and src != "-" and not re.match(r"^https://\S+$", src):
            findings.append((path, n, "error", "G05", "URL column of '%s' is not an https:// URL or -" % term))
        al = [] if aliases in ("", "-") else [a.strip() for a in aliases.split(",") if a.strip()]
        entries.append((n, term, al))
    return kinds, entries, lines, findings


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, x) for x in sorted(names) if x.endswith(".md")]
        else:
            files.append(p)
    return files


def check(paths):
    findings = []
    ref_seen, prj_seen = {}, {}
    for path in collect(paths):
        kinds, entries, lines, f = parse(path)
        findings += f
        if not kinds:
            continue
        is_ref = "ref" in kinds
        if is_ref and not any(VERIFIED_RE.search(x) for x in lines[:8]):
            findings.append((path, 1, "error", "G07", "no 'verified YYYY-MM-DD' line in the first 8 lines"))
        seen = ref_seen if is_ref else prj_seen
        local = {}
        for n, term, al in entries:
            names = [term] + al
            row = set()
            for name in names:
                k = norm(name)
                if not k or k in row:
                    continue
                row.add(k)
                store = seen if is_ref else local
                if k in store:
                    pf, pn = store[k]
                    findings.append((path, n, "error", "G06", "'%s' already defined at %s:%d" % (name, os.path.basename(pf), pn)))
                else:
                    store[k] = (path, n)
        if not is_ref:
            for k, loc in local.items():
                prj_seen.setdefault(k, loc)
    for k, (pf, pn) in prj_seen.items():
        if k in ref_seen:
            findings.append((pf, pn, "warning", "G08", "'%s' also appears in %s; the project entry wins" % (k, os.path.basename(ref_seen[k][0]))))
    return findings


def report(findings):
    for path, n, level, code, msg in sorted(findings, key=lambda x: (x[0], x[1])):
        print("%s:%d: %s %s %s" % (path, n, level, code, msg))
    return 1 if any(f[2] == "error" for f in findings) else 0


REF_OK = """# T

verified 2026-11-04

| term | aliases | what it is | not to confuse with | official URL |
|---|---|---|---|---|
| Alpha | A, Aleph | A thing | Beta | https://example.com/ |
| Beta | formerly Gamma | Another thing | Alpha | - |
"""


def self_test():
    cases = [
        ("ok", REF_OK, set()),
        ("G01", REF_OK + "| Delta | x | y | z |\n", {"G01"}),
        ("G02", REF_OK.replace("official URL", "link"), {"G02"}),
        ("G03", REF_OK + "| Eps | - | - | Alpha | - |\n", {"G03"}),
        ("G04", REF_OK + "| Zeta | - | meaning | | - |\n", {"G04"}),
        ("G05", REF_OK + "| Eta | - | meaning | - | http://example.com/ |\n", {"G05"}),
        ("G06 alias", REF_OK + "| Theta | aleph | meaning | - | - |\n", {"G06"}),
        ("G06 formerly", REF_OK + "| Gamma | - | meaning | - | - |\n", {"G06"}),
        ("G07", REF_OK.replace("verified 2026-11-04", "checked"), {"G07"}),
    ]
    failed = 0
    with tempfile.TemporaryDirectory() as d:
        for name, text, want in cases:
            p = os.path.join(d, "terms-t.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            got = {f[3] for f in check([p]) if f[2] == "error"}
            ok = got == want
            failed += not ok
            print("%s %s (want %s, got %s)" % ("ok  " if ok else "FAIL", name, sorted(want), sorted(got)))
        # project file: duplicate inside the file is an error, overlap with a reference only a warning
        prj = "| term | aliases | meaning in this project | not to confuse with | source |\n|---|---|---|---|---|\n| Alpha | - | our alpha | - | docs/a.md |\n"
        rp = os.path.join(d, "terms-t.md")
        with open(rp, "w", encoding="utf-8") as fh:
            fh.write(REF_OK)
        pp = os.path.join(d, "GLOSSARY.md")
        with open(pp, "w", encoding="utf-8") as fh:
            fh.write(prj)
        f = check([rp, pp])
        ok = {x[3] for x in f} == {"G08"} and not any(x[2] == "error" for x in f)
        failed += not ok
        print("%s project overlap is a warning" % ("ok  " if ok else "FAIL"))
        with open(pp, "w", encoding="utf-8") as fh:
            fh.write(prj + "| alpha | - | again | - | - |\n")
        ok = any(x[3] == "G06" for x in check([pp]))
        failed += not ok
        print("%s project duplicate is an error" % ("ok  " if ok else "FAIL"))
    print("self-test: %s" % ("passed" if not failed else "%d failed" % failed))
    return 1 if failed else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    paths = a.paths or [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")]
    for p in paths:
        if not os.path.exists(p):
            print("no such path: %s" % p, file=sys.stderr)
            return 2
    return report(check(paths))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
