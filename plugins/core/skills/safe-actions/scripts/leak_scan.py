#!/usr/bin/env python3
"""Scan a repository for internals that must not go public: personal paths, secrets, chat and
transcript residue, private network names and a private term list.

Usage:
  leak_scan.py [ROOT] [--history] [--terms FILE]
  leak_scan.py --self-test

ROOT defaults to the current directory. The scan reads git-tracked files when ROOT is a git work tree,
otherwise every file under ROOT except .git, node_modules and vendor. Binary files and files over 2 MB
are skipped. --history also reads every line ever added in the history of all refs (git log -p), since
publishing a repository publishes its history. --terms FILE adds private terms, one per line (names
of people, customers, internal projects or hosts); the LEAK_TERMS environment variable adds more,
separated by commas. Terms are matched case-insensitively and never printed.

Findings (code, level, what it means):
  P01 error    an absolute path into a personal home directory (Linux home, macOS Users, Windows
               Users folder); placeholder names such as user, runner, me, you, example and [user] pass
  P02 error    a secret: private key block, cloud or forge access token
  P03 error    a private term from --terms or LEAK_TERMS
  P04 warning  chat or transcript residue: speaker prefixes ("Assistant:", "Human:"), "as you said",
               "in our conversation", session summaries
  P05 warning  a private network address (RFC 1918) or an internal host name (*.internal, *.lan,
               *.corp, *.intranet, *.home.arpa)

A deliberate match (a fake key in a test fixture) passes with a comment "leak-scan: allow P02 [reason]"
on the same or the previous line; the reason is required.

Output: one finding per line as "path:line: level code message"; history findings name the commit
as "commit:SHA". Exit 0 when there is no error, 1 otherwise, 2 on a usage error. A clean run means
these patterns were not found; it does not replace reading what is about to be published. Python 3.8
or later, standard library only, no network.
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", ".venv"}
MAX_BYTES = 2_000_000
PLACEHOLDERS = {"user", "username", "runner", "me", "you", "example", "name", "your-name", "yourname", "dev",
                "ubuntu", "root", "node", "app", "[user]", "[name]", "$user", "${user}", "<user>", "..."}

# lint-allow: L09 the scanner's own pattern for personal paths
HOME_RE = re.compile(r"(?:/home/|/Users/|\b[A-Za-z]:\\Users\\)([A-Za-z0-9_][\w.-]*)")
SECRET_RES = [
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bsk-(?:proj-|live_|ant-)?[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
]
CHAT_RES = [
    re.compile(r"^\s*(?:>\s*)?\**(?:Human|Assistant|Claude|ChatGPT|Copilot)\**\s*:\s+\S"),
    re.compile(r"\bas (?:you|I) (?:said|mentioned|asked|requested)\b", re.I),
    re.compile(r"\bin (?:our|the previous|the last) (?:chat|conversation|session)\b", re.I),
    re.compile(r"\b(?:session|conversation|chat) (?:summary|transcript|log)\b", re.I),
    re.compile(r"\bas an AI(?: language model)?\b", re.I),
]
PRIVATE_IP_RE = re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")
INTERNAL_HOST_RE = re.compile(r"\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:internal|lan|corp|intranet|home\.arpa)\b",
                              re.I)


def load_terms(terms_file: str | None) -> list[str]:
    terms: list[str] = []
    if terms_file:
        for line in Path(terms_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    terms += [t.strip() for t in os.environ.get("LEAK_TERMS", "").split(",") if t.strip()]
    return terms


ALLOW_RE = re.compile(r"leak-scan:\s*allow\s+(P0\d)\s+\S")


def term_patterns(terms: list[str]) -> list[re.Pattern]:
    return [re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.I) for t in terms]


def scan_line(line: str, term_res: list[re.Pattern], prev: str = "") -> list[tuple[str, str, str]]:
    allowed = {m.group(1) for m in ALLOW_RE.finditer(line + "\n" + prev)}
    return [f for f in raw_findings(line, term_res) if f[1] not in allowed]


def raw_findings(line: str, term_res: list[re.Pattern]) -> list[tuple[str, str, str]]:
    out = []
    for m in HOME_RE.finditer(line):
        if m.group(1).lower() not in PLACEHOLDERS:
            out.append(("error", "P01", "absolute personal path"))
            break
    if any(rx.search(line) for rx in SECRET_RES):
        out.append(("error", "P02", "secret or access token"))
    for k, rx in enumerate(term_res):
        if rx.search(line):
            out.append(("error", "P03", f"private term #{k + 1}"))
    if any(rx.search(line) for rx in CHAT_RES):
        out.append(("warning", "P04", "chat or transcript residue"))
    if PRIVATE_IP_RE.search(line) or INTERNAL_HOST_RE.search(line):
        out.append(("warning", "P05", "private network address or internal host name"))
    return out


def tracked_files(root: Path) -> list[Path]:
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout:
            return [root / p for p in r.stdout.split("\0") if p]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return [p for p in root.rglob("*")
            if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)]


def read_text(p: Path) -> str | None:
    try:
        if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
            return None
        data = p.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def history_lines(root: Path):
    r = subprocess.run(["git", "-C", str(root), "log", "--all", "-p", "--no-color", "--no-ext-diff",
                        "--format=commit:%H"], capture_output=True, text=True, errors="replace", timeout=600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git log failed")
    sha, prev = "?", ""
    for line in r.stdout.splitlines():
        if line.startswith("commit:"):
            sha, prev = line[7:19], ""
        elif line.startswith("+"):
            yield sha, line[1:], prev
            prev = line[1:]
        else:
            prev = line[1:]


def run(root: Path, history: bool, terms: list[str], out=print) -> int:
    term_res = term_patterns(terms)
    errors = 0
    for p in sorted(tracked_files(root)):
        text = read_text(p)
        if text is None:
            continue
        rel = p.relative_to(root).as_posix()
        lines = text.splitlines()
        for n, line in enumerate(lines, 1):
            for level, code, msg in scan_line(line, term_res, lines[n - 2] if n > 1 else ""):
                out(f"{rel}:{n}: {level} {code} {msg}")
                errors += level == "error"
    if history:
        seen = set()
        for sha, line, prev in history_lines(root):
            for level, code, msg in scan_line(line, term_res, prev):
                key = (sha, code, line)
                if key in seen:
                    continue
                seen.add(key)
                out(f"commit:{sha}: {level} {code} {msg} (in history)")
                errors += level == "error"
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)
    history = "--history" in args
    if history:
        args.remove("--history")
    terms_file = None
    if "--terms" in args:
        i = args.index("--terms")
        if i + 1 >= len(args):
            print("--terms needs a file", file=sys.stderr)
            return 2
        terms_file = args[i + 1]
        del args[i:i + 2]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print(__doc__.split("Findings")[0].strip(), file=sys.stderr)
        return 2
    root = Path(args[0]) if args else Path(".")
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    try:
        terms = load_terms(terms_file)
        return run(root, history, terms)
    except (OSError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def self_test() -> int:
    fails = []

    def check(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    def codes(line, terms=()):
        return [c for _, c, _ in scan_line(line, term_patterns(terms))]

    home = "/" + "home/"
    check("personal home path", codes(f"see {home}alice/projects/app/README.md"), ["P01"])
    check("mac home path", codes("open /" + "Users/bob/Desktop/x"), ["P01"])
    check("windows home path", codes("C:" + "\\Users\\carol\\repo"), ["P01"])
    check("placeholder home path", codes(f"cache in {home}runner/.cache and {home}[user]/x"), [])
    check("private key", codes("-----BEGIN OPENSSH " + "PRIVATE KEY-----"), ["P02"])
    check("forge token", codes("token: gh" + "p_" + "a" * 36), ["P02"])
    check("cloud key id", codes("AKIA" + "ABCDEFGHIJKLMNOP"), ["P02"])
    check("private term", codes("Thanks to Acme Rockets for the data", ["acme rockets"]), ["P03"])
    check("term needs word boundary", codes("see acmesoft.example", ["acme"]), [])
    check("term needs leading boundary", codes("see notacme here", ["acme"]), [])
    check("separator after home is no path", codes("paths such as (/" + "home/, /" + "Users/)"), [])
    check("allow comment with reason", [c for _, c, _ in scan_line("k = '-----BEGIN RSA " + "PRIVATE KEY-----'", [],
                                                                    "# leak-scan: allow P02 fake key for the test")], [])
    check("allow comment needs reason", [c for _, c, _ in scan_line("-----BEGIN RSA " + "PRIVATE KEY-----", [],
                                                                     "# leak-scan: allow P02")], ["P02"])
    check("speaker prefix", codes("Assistant: here is the plan"), ["P04"])
    check("chat reference", codes("As you said in our conversation, keep it small."), ["P04"])
    check("persona prose is fine", codes("User: project lead. Nothing ships unless the user asked."), [])
    check("private ip", codes("db at 10.0" + ".3.7"), ["P05"])
    check("internal host", codes("push to registry.corp:5000"), ["P05"])
    check("documentation ip is fine", codes("listen on 192.0" + ".2.10"), [])
    check("neutral prose", codes("Run make test before you open a pull request."), [])

    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / "README.md").write_text("# Demo\n", encoding="utf-8")
        (root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        (root / "notes.md").write_text(f"built in {home}dave/src\n", encoding="utf-8")
        (root / "node_modules").mkdir()
        (root / "node_modules" / "x.js").write_text(f"// {home}erin/x\n", encoding="utf-8")
        (root / "blob.bin").write_bytes(b"\0" + f"{home}frank/".encode())
        lines: list[str] = []
        check("tree exit", run(root, False, [], lines.append), 1)
        check("tree findings", lines, ["notes.md:1: error P01 absolute personal path"])

        git = ["git", "-C", str(root), "-c", "user.email=t@example.org", "-c", "user.name=t"]
        if subprocess.run(git + ["init", "-q"], capture_output=True).returncode == 0:
            (root / "notes.md").write_text("The user asked for a smaller modal.\n", encoding="utf-8")
            subprocess.run(git + ["add", "-A"], capture_output=True)
            subprocess.run(git + ["commit", "-qm", "first"], capture_output=True)
            subprocess.run(git + ["checkout", "-qb", "side"], capture_output=True)
            (root / "a.md").write_text(f"built in {home}dave/src\n", encoding="utf-8")
            (root / "b.md").write_text(f"built in {home}dave/src\n", encoding="utf-8")
            subprocess.run(git + ["add", "-A"], capture_output=True)
            subprocess.run(git + ["commit", "-qm", "leak on a side branch"], capture_output=True)
            subprocess.run(git + ["checkout", "-q", "-"], capture_output=True)
            check("warning-only tree passes", run(root, False, [], lambda *_: None), 0)
            hist: list[str] = []
            check("history of all refs leaks", run(root, True, [], hist.append), 1)
            check("history finding per commit and line",
                  [h.split(": ", 1)[1] for h in hist if "P01" in h], ["error P01 absolute personal path (in history)"])
        else:
            fails.append("git is not available for the history case")
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
