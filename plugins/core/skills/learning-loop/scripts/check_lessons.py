#!/usr/bin/env python3
"""Check a lesson store: frontmatter, Why and How to apply, secrets, index limits, links.

Usage:
  check_lessons.py [STORE] [--index FILE]
  check_lessons.py --self-test

STORE is a directory of lesson files (default: docs/lessons, else the auto-memory style directory given).
The index is INDEX.md or MEMORY.md inside STORE unless --index names one.

Checks (code, level, what fails):
  L01 error    STORE is missing or holds no lesson file
  L02 error    a lesson has no frontmatter, or lacks name, description or type
  L03 error    `name` differs from the file name without .md
  L04 error    `type` is not one of feedback, project, reference, user
  L05 error    a feedback or project lesson has no **Why:** or no **How to apply:** line
  L06 error    a secret-shaped string (private key block, AWS key id, GitHub or Slack token, bearer
               token, password or api key assignment with a literal value, credentials in a URL)
  L07 error    the index is over 200 lines or 25,000 bytes (the load limit of Claude Code auto memory)
  L08 error    a lesson file has no line in the index, or an index line points to a missing file
  L09 warning  an index line is over 150 characters
  L10 warning  a link to another lesson ([[name]] or a relative .md link) points to nothing
  L11 warning  a project lesson has no date (YYYY-MM-DD) anywhere in the file
  L12 warning  a reference or user lesson has an e-mail address or an IBAN-shaped string

Exit 0 when no error, 1 with errors, 2 on a usage error. Python 3.8 or later, standard library only, no network.
It finds secret-shaped strings, not all secrets. A clean result does not prove a store is free of sensitive data.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

TYPES = {"feedback", "project", "reference", "user"}
INDEX_NAMES = ("INDEX.md", "MEMORY.md")
MAX_INDEX_LINES = 200
MAX_INDEX_BYTES = 25000
MAX_INDEX_LINE = 150

SECRET_RES = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("API key style token", re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b|\bsk-[A-Za-z0-9]{20,}\b")),
    ("credentials in a URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]{3,}@[^\s/]+")),
    ("assigned secret",
     re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*[:=]\s*[\"']?(?!<|\[|\$|\{|your|example|changeme|xxx|\.\.\.|none|null)[A-Za-z0-9!@#$%^&*_+=./-]{8,}")),
]
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}(?:\s?[A-Z0-9]{1,4})?\b")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
WIKI_RE = re.compile(r"\[\[([^\]]+)\]\]")
MDLINK_RE = re.compile(r"\]\(\s*<?([^)\s>#]+\.md)(?:#[^)]*)?>?\s*\)")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, path, code, msg):
        self.errors.append(f"{path}: {code} {msg}")

    def warn(self, path, code, msg):
        self.warnings.append(f"{path}: {code} {msg}")


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return None, text
    head = parts[0][3:].strip("\n")
    body = parts[1].lstrip("-").lstrip("\n")
    data = {}
    stack_key = None
    for line in head.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        indent, key, val = m.groups()
        val = val.strip().strip('"').strip("'")
        if indent and stack_key == "metadata":
            data[key] = val
        else:
            data[key] = val
            stack_key = key
    return data, body


def find_index(store, explicit):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    for n in INDEX_NAMES:
        p = os.path.join(store, n)
        if os.path.isfile(p):
            return p
    return None


def check(store, index_path=None):
    r = Report()
    if not os.path.isdir(store):
        r.err(store, "L01", "store directory not found")
        return r
    index = find_index(store, index_path)
    files = sorted(f for f in os.listdir(store)
                   if f.endswith(".md") and os.path.join(store, f) != index and f not in INDEX_NAMES)
    if not files:
        r.err(store, "L01", "no lesson files in the store")
    names = {f[:-3] for f in files}

    for f in files:
        path = os.path.join(store, f)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        data, body = split_frontmatter(text)
        if data is None or not all(data.get(k) for k in ("name", "description", "type")):
            r.err(f, "L02", "frontmatter with name, description and type is required")
        else:
            if data["name"] != f[:-3]:
                r.err(f, "L03", f"name '{data['name']}' differs from the file name")
            if data["type"] not in TYPES:
                r.err(f, "L04", f"type '{data['type']}' is not one of {', '.join(sorted(TYPES))}")
            if data["type"] in ("feedback", "project"):
                if not re.search(r"\*\*Why:?\*\*", body):
                    r.err(f, "L05", "missing **Why:** line")
                if not re.search(r"\*\*How to apply:?\*\*", body):
                    r.err(f, "L05", "missing **How to apply:** line")
            if data["type"] == "project" and not DATE_RE.search(text):
                r.warn(f, "L11", "project lesson has no date")
            if data["type"] in ("reference", "user") and (EMAIL_RE.search(body) or IBAN_RE.search(body)):
                r.warn(f, "L12", "e-mail address or IBAN-shaped string in the lesson")
        for label, rx in SECRET_RES:
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    r.err(f"{f}:{i}", "L06", f"secret-shaped string ({label}); store where it lives, not the value")
                    break
        for m in WIKI_RE.finditer(text):
            if m.group(1).strip() not in names:
                r.warn(f, "L10", f"link [[{m.group(1)}]] points to no lesson")
        for m in MDLINK_RE.finditer(text):
            target = os.path.normpath(os.path.join(store, m.group(1)))
            if not m.group(1).startswith(("http://", "https://")) and not os.path.exists(target):
                r.warn(f, "L10", f"link {m.group(1)} points to nothing")

    if index:
        raw = open(index, "rb").read()
        lines = raw.decode("utf-8", errors="replace").splitlines()
        if len(lines) > MAX_INDEX_LINES or len(raw) > MAX_INDEX_BYTES:
            r.err(os.path.basename(index), "L07",
                  f"index has {len(lines)} lines and {len(raw)} bytes (limit {MAX_INDEX_LINES} lines or {MAX_INDEX_BYTES} bytes)")
        indexed = set()
        for i, line in enumerate(lines, 1):
            if len(line) > MAX_INDEX_LINE and line.lstrip().startswith("-"):
                r.warn(f"{os.path.basename(index)}:{i}", "L09", f"index line has {len(line)} characters")
            for m in MDLINK_RE.finditer(line):
                target = m.group(1)
                if target.startswith(("http://", "https://")):
                    continue
                base = os.path.basename(target)
                indexed.add(base)
                if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(index), target))):
                    r.err(f"{os.path.basename(index)}:{i}", "L08", f"index points to missing file {target}")
        for f in files:
            if f not in indexed:
                r.err(f, "L08", "lesson has no line in the index")
    else:
        for f in files:
            r.err(f, "L08", "no index file (INDEX.md or MEMORY.md) in the store")
    return r


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


GOOD = """---
name: formatter-own-files-only
description: Run a formatter only on the files you changed, passed by name
type: feedback
---

Run the formatter only on files you changed.

**Why:** A directory-wide run rewrote two files someone else was editing. (2026-10-04)

**How to apply:** Build the file list from git status first. Related: [[other-lesson]]
"""
OTHER = GOOD.replace("formatter-own-files-only", "other-lesson").replace(" Related: [[other-lesson]]", "")
INDEX = ("- [Formatter on own files](formatter-own-files-only.md): any formatter run\n"
         "- [Other](other-lesson.md): when other things happen\n")


def self_test():
    ok = True

    def run(files, index=INDEX):
        with tempfile.TemporaryDirectory() as d:
            for name, text in files.items():
                write(os.path.join(d, name), text)
            if index is not None:
                write(os.path.join(d, "INDEX.md"), index)
            return check(d)

    def expect(label, files, code=None, level="errors", index=INDEX):
        nonlocal ok
        rep = run(files, index)
        found = [x for x in getattr(rep, level) if f" {code} " in x] if code else (rep.errors + rep.warnings)
        if code and not found:
            print(f"self-test: {label}: expected {code}, got {rep.errors + rep.warnings}")
            ok = False
        if not code and found:
            print(f"self-test: {label}: expected clean, got {found}")
            ok = False

    base = {"formatter-own-files-only.md": GOOD, "other-lesson.md": OTHER}
    expect("clean store", base)
    expect("L01 empty store", {}, "L01")
    expect("L02 no frontmatter", {**base, "formatter-own-files-only.md": "Just text"}, "L02")
    expect("L03 name mismatch", {**base, "other-lesson.md": OTHER.replace("name: other-lesson", "name: wrong")}, "L03")
    expect("L04 bad type", {**base, "other-lesson.md": OTHER.replace("type: feedback", "type: opinion")}, "L04")
    expect("L05 no why", {**base, "other-lesson.md": OTHER.replace("**Why:**", "Because")}, "L05")
    expect("L05 no how", {**base, "other-lesson.md": OTHER.replace("**How to apply:**", "Do")}, "L05")
    for label, secret in (
        ("aws", "key AK" + "IAABCDEFGHIJKLMNOP"),
        ("github", "token ghp_" + "a" * 36),
        ("password", "password: hunter2hunter2"),
        ("url", "db postgres://admin:s3cretpass@db.example.com/app"),
        ("key block", "-----BEGIN RSA PRIVATE KEY-----"),
        ("bearer", "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123"),
    ):
        expect(f"L06 {label}", {**base, "other-lesson.md": OTHER + "\n" + secret + "\n"}, "L06")
    expect("L06 placeholder is fine", {**base, "other-lesson.md": OTHER + "\npassword: <from the secret manager>\n"})
    expect("L07 long index", base, "L07", index=INDEX + "\n".join(f"- line {i}" for i in range(210)) + "\n")
    expect("L08 missing from index", base, "L08", index="- [Other](other-lesson.md): x\n")
    expect("L08 dead index line", base, "L08", index=INDEX + "- [Gone](gone.md): x\n")
    expect("L09 long index line", base, "L09", level="warnings", index=INDEX + "- [Other](other-lesson.md): " + "x" * 160 + "\n")
    expect("L10 dead link", {**base, "other-lesson.md": OTHER + "\nSee [[nope]]\n"}, "L10", level="warnings")
    project = OTHER.replace("type: feedback", "type: project").replace(" (2026-10-04)", "")
    expect("L11 project without date", {**base, "other-lesson.md": project}, "L11", level="warnings")
    ref = "---\nname: other-lesson\ndescription: where things are\ntype: reference\n---\n\nAsk jane.doe@" + "corp.test.\n"
    expect("L12 e-mail in reference", {**base, "other-lesson.md": ref}, "L12", level="warnings")
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("store", nargs="?")
    ap.add_argument("--index")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    store = args.store or "docs/lessons"
    rep = check(store, args.index)
    for line in rep.warnings + rep.errors:
        print(line)
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
