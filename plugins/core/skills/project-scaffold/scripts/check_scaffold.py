#!/usr/bin/env python3
"""Check a scaffolded repository against the Scaffold table in docs/PROJECT-FACTS.md.

Usage:
  check_scaffold.py [ROOT] [--facts FILE]
  check_scaffold.py --self-test

ROOT defaults to the current directory. FILE defaults to docs/PROJECT-FACTS.md under ROOT.

The table sits under a heading "## Scaffold" with the columns Component | Directory | Starter |
Version | Flags. Directory "." means the repository root.

Checks (code, level, what fails):
  S01 error    no "## Scaffold" table, or it has no rows
  S02 error    a row has no directory, starter or version, or the version is not pinned
               (empty, "latest", "*", or no number like 13.17)
  S03 error    a row's directory does not exist
  S04 error    a directory does not look like its starter's output (Laravel, Laravel Vue kit,
               Nuxt, Go); warning when the starter has no known fingerprint
  S05 error    a component manifest (composer.json, package.json, go.mod, Cargo.toml,
               pyproject.toml) sits outside every listed directory: a component nobody approved
  S06 error    Laravel: Flags pass --database=X but .env.example has another DB_CONNECTION
  S07 warning  Laravel: composer.json pins no runtime in config.platform.php
  S08 warning  git history exists, but no commit subject starting "chore: scaffold" touches the
               directory (the untouched first commit is missing)

Output: one finding per line as "path:line: level code message". Exit 0 when there is no error,
1 otherwise, 2 on a usage error. Python 3.8 or later, standard library only, no network.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MANIFESTS = ("composer.json", "package.json", "go.mod", "Cargo.toml", "pyproject.toml")
SKIP = {".git", "node_modules", "vendor", ".nuxt", ".output", "dist", "build", "storage", "bootstrap",
        "public", ".venv", "venv", "__pycache__", "docs"}
PINNED = re.compile(r"\d+\.\d+")


def read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def parse_table(text: str):
    """Return (heading_line, rows) for the table under '## Scaffold'; rows carry their line number."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"^##\s+Scaffold\b", l.strip(), re.I)), None)
    if start is None:
        return None, []
    header, rows = None, []
    for i in range(start + 1, len(lines)):
        l = lines[i].strip()
        if l.startswith("#"):
            break
        if not l.startswith("|"):
            if header and rows:
                break
            continue
        cells = [c.strip().strip("`") for c in l.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        row = dict(zip(header, cells))
        row["_line"] = i + 1
        rows.append(row)
    return start + 1, rows


def fingerprint(starter: str, d: Path) -> tuple[str, str] | None:
    """Return (level, message) when the directory does not match the starter."""
    s = starter.lower()
    comp = read_json(d / "composer.json")
    pkg = read_json(d / "package.json")
    req = {**comp.get("require", {}), **comp.get("require-dev", {})}
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    if "laravel" in s:
        need = ["laravel/framework"]
        need_js: list[str] = []
        if "vue" in s:
            need += ["inertiajs/inertia-laravel", "laravel/fortify"]
            need_js = ["vue", "@inertiajs/vue3"]
        missing = [n for n in need if n not in req] + [n for n in need_js if n not in deps]
        return ("error", f"not a {starter} skeleton: missing {', '.join(missing)}") if missing else None
    if "nuxt" in s:
        return None if "nuxt" in deps else ("error", "not a Nuxt skeleton: package.json has no nuxt dependency")
    if re.search(r"\bgo\b", s):
        return None if (d / "go.mod").is_file() else ("error", "not a Go module: go.mod is missing")
    return ("warning", f"starter '{starter}' has no known fingerprint; not checked")


def manifests(root: Path) -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith(".") and rel_depth < 3]
        if any(f in filenames for f in MANIFESTS):
            found.append(Path(dirpath))
    return found


def git_subjects(root: Path, d: Path) -> list[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        r = subprocess.run(["git", "-C", str(root), "log", "--format=%s", "--", str(d.relative_to(root)) or "."],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.splitlines() if r.returncode == 0 else None


def check(root: Path, facts: Path) -> list[tuple[str, int, str, str, str]]:
    out: list[tuple[str, int, str, str, str]] = []
    try:
        frel = str(facts.relative_to(root))
    except ValueError:
        frel = str(facts)

    def f(path, line, level, code, msg):
        out.append((path, line, level, code, msg))

    if not facts.is_file():
        f(frel, 0, "error", "S01", "facts file not found; add a '## Scaffold' table")
        return out
    head, rows = parse_table(facts.read_text(encoding="utf-8"))
    if head is None or not rows:
        f(frel, head or 0, "error", "S01", "no '## Scaffold' table with rows")
        return out

    listed: list[Path] = []
    for row in rows:
        ln = row["_line"]
        comp = row.get("component", "") or "?"
        dname, starter = row.get("directory", ""), row.get("starter", "")
        version, flags = row.get("version", ""), row.get("flags", "")
        if not dname or not starter:
            f(frel, ln, "error", "S02", f"{comp}: directory and starter are required")
            continue
        if not version or "latest" in version.lower() or version.strip() in {"*", "x"} or not PINNED.search(version):
            f(frel, ln, "error", "S02", f"{comp}: version '{version}' is not pinned")
        d = (root / dname).resolve()
        listed.append(d)
        if not d.is_dir():
            f(frel, ln, "error", "S03", f"{comp}: directory '{dname}' does not exist")
            continue
        fp = fingerprint(starter, d)
        if fp:
            f(dname, 0, fp[0], "S04", f"{comp}: {fp[1]}")
        if "laravel" in starter.lower():
            m = re.search(r"--database[= ](\w+)", flags)
            env = d / ".env.example"
            if m and env.is_file():
                cur = re.search(r"^DB_CONNECTION=(\w+)", env.read_text(encoding="utf-8"), re.M)
                if not cur or cur.group(1) != m.group(1):
                    f(str(env.relative_to(root)), 0, "error", "S06",
                      f"{comp}: DB_CONNECTION is '{cur.group(1) if cur else 'unset'}', flags say '{m.group(1)}'")
            plat = read_json(d / "composer.json").get("config", {}).get("platform", {})
            if "php" not in plat:
                f(str((d / "composer.json").relative_to(root)), 0, "warning", "S07",
                  f"{comp}: no config.platform.php; pin the production PHP version")
        subj = git_subjects(root, d)
        if subj is not None and not any(s.lower().startswith("chore: scaffold") for s in subj):
            f(dname, 0, "warning", "S08", f"{comp}: no 'chore: scaffold' commit touches this directory")

    for m in manifests(root):
        if not any(m == d or d in m.parents for d in listed):
            names = ", ".join(x for x in MANIFESTS if (m / x).is_file())
            f(str(m.relative_to(root)) or ".", 0, "error", "S05",
              f"component ({names}) not in the Scaffold table; remove it or get it approved and list it")
    return out


# ---------------------------------------------------------------- self-test

FACTS = """# Project facts

## Scaffold

| Component | Directory | Starter | Version | Flags |
|---|---|---|---|---|
| App | app | Laravel Vue starter kit | installer 5.32.0, laravel/framework 13.17 | --vue --pest --database=pgsql -n |
"""

APP = {
    "app/composer.json": json.dumps({"require": {"laravel/framework": "^13.17", "inertiajs/inertia-laravel": "^3.0",
                                                 "laravel/fortify": "^1.37"},
                                     "config": {"platform": {"php": "8.4.0"}}}),
    "app/package.json": json.dumps({"dependencies": {"vue": "^3.5", "@inertiajs/vue3": "^3.0"}}),
    "app/.env.example": "APP_NAME=Demo\nDB_CONNECTION=pgsql\n",
    "docs/PROJECT-FACTS.md": FACTS,
}


def build(tmp: Path, files: dict) -> None:
    for rel, content in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def self_test() -> int:
    cases = []

    def case(name, overrides, expect, absent=()):
        cases.append((name, overrides, set(expect), set(absent)))

    case("good scaffold passes", {}, [], ["S01", "S02", "S03", "S04", "S05", "S06", "S07"])
    case("no table", {"docs/PROJECT-FACTS.md": "# Project facts\n"}, ["S01"])
    case("unpinned version", {"docs/PROJECT-FACTS.md": FACTS.replace("installer 5.32.0, laravel/framework 13.17", "latest")},
         ["S02"])
    case("major-only version", {"docs/PROJECT-FACTS.md": FACTS.replace("installer 5.32.0, laravel/framework 13.17", "Laravel 13")},
         ["S02"])
    case("missing directory", {"docs/PROJECT-FACTS.md": FACTS.replace("| app |", "| api |")}, ["S03"])
    case("hand-built app fails fingerprint",
         {"app/composer.json": json.dumps({"require": {"laravel/framework": "^13.0"},
                                           "config": {"platform": {"php": "8.4.0"}}})}, ["S04"])
    case("unapproved second component", {"site/package.json": json.dumps({"dependencies": {"nuxt": "^4.6"}})},
         ["S05"])
    case("unapproved go worker", {"worker/go.mod": "module example.org/worker\n\ngo 1.27\n"}, ["S05"])
    case("database drift", {"app/.env.example": "DB_CONNECTION=sqlite\n"}, ["S06"])
    case("no runtime pin warns",
         {"app/composer.json": json.dumps({"require": {"laravel/framework": "^13.17",
                                                       "inertiajs/inertia-laravel": "^3.0", "laravel/fortify": "^1"}})},
         ["S07"])
    case("listed nuxt site passes",
         {"site/package.json": json.dumps({"dependencies": {"nuxt": "^4.6"}}),
          "docs/PROJECT-FACTS.md": FACTS + "| Site | site | Nuxt (create-nuxt, minimal) | create-nuxt 4.0.3, nuxt 4.6 | --template minimal |\n"},
         [], ["S04", "S05"])
    case("root component", {"composer.json": APP["app/composer.json"], "package.json": APP["app/package.json"],
                            ".env.example": APP["app/.env.example"], "app/composer.json": None, "app/package.json": None,
                            "app/.env.example": None,
                            "docs/PROJECT-FACTS.md": FACTS.replace("| app |", "| . |")},
         [], ["S03", "S04", "S05"])

    failed = 0
    for name, overrides, expect, absent in cases:
        files = dict(APP)
        for k, v in overrides.items():
            if v is None:
                files.pop(k, None)
            else:
                files[k] = v
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            build(root, files)
            got = {code for _, _, _, code, _ in check(root, root / "docs" / "PROJECT-FACTS.md")}
        if not expect <= got or (absent and got & set(absent)):
            failed += 1
            print(f"FAIL {name}: got {sorted(got)}, want {sorted(expect)}, not {sorted(absent)}")
    if failed:
        print(f"self-test: {failed} of {len(cases)} case(s) failed")
        return 1
    print(f"self-test: {len(cases)} case(s) ok")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)
    facts_arg = None
    if "--facts" in args:
        i = args.index("--facts")
        if i + 1 >= len(args):
            print("usage: check_scaffold.py [ROOT] [--facts FILE]", file=sys.stderr)
            return 2
        facts_arg = args[i + 1]
        del args[i:i + 2]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print("usage: check_scaffold.py [ROOT] [--facts FILE]", file=sys.stderr)
        return 2
    root = Path(args[0] if args else ".").resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    facts = (root / facts_arg) if facts_arg else root / "docs" / "PROJECT-FACTS.md"
    findings = check(root, facts.resolve())
    for path, line, level, code, msg in findings:
        print(f"{path}:{line}: {level} {code} {msg}")
    errors = sum(1 for x in findings if x[2] == "error")
    warns = len(findings) - errors
    print(f"{errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
