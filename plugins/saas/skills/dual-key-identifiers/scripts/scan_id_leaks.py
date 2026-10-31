#!/usr/bin/env python3
"""Scan captured JSON payloads for internal (sequential) record IDs.

Reads JSON or JSONL files: guard report output, webhook bodies, broadcast and
mail payload dumps, JSON exports. Flags integer or digit-only values under keys
named id, *_id, *Id, *_ids, *Ids; decodes base64url JSON cursors; flags URL
values with a digit-only path segment. Python standard library only, no
network.

Exit codes: 0 clean, 1 leaks found, 2 usage or input error.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import fnmatch
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ID_KEY = re.compile(r"^(id|.+_id|.+Id|.+_ids|.+Ids|ids)$")
URL_KEY = re.compile(r"(^|_)(url|href|link|location)$|(Url|Href|Link)$", re.I)
CURSOR_KEY = re.compile(r"cursor", re.I)
DIGITS = re.compile(r"^\d+$")


def is_internal(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, str) and DIGITS.match(value):
        return True
    if isinstance(value, list):
        return any(is_internal(v) for v in value)
    return False


def decode_cursor(text: str):
    """Return the JSON object inside a base64url cursor, or None."""
    if len(text) < 8 or not re.match(r"^[A-Za-z0-9_\-+/=]+$", text):
        return None
    padded = text.replace("-", "+").replace("_", "/")
    padded += "=" * (-len(padded) % 4)
    try:
        data = json.loads(base64.b64decode(padded, validate=True))
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None
    return data if isinstance(data, (dict, list)) else None


class Scanner:
    def __init__(self, allow: list[tuple[str, str]]) -> None:
        self.allow = allow
        self.findings: list[str] = []

    def allowed(self, key: str, path: str) -> bool:
        return any(fnmatch.fnmatchcase(key, pat) or fnmatch.fnmatchcase(path, pat) for pat, _ in self.allow)

    def report(self, where: str, path: str, why: str) -> None:
        self.findings.append(f"{where}: {path}: {why}")

    def walk(self, node, where: str, path: str = "$") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                key = str(key)
                sub = f"{path}.{key}"
                if self.allowed(key, sub):
                    continue
                if ID_KEY.match(key) and is_internal(value):
                    self.report(where, sub, "internal ID value under an ID key")
                if isinstance(value, str):
                    self.check_string(key, value, where, sub)
                self.walk(value, where, sub)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                self.walk(value, where, f"{path}[{i}]")

    def check_string(self, key: str, value: str, where: str, path: str) -> None:
        if CURSOR_KEY.search(key):
            inner = decode_cursor(value)
            if inner is not None:
                self.walk(inner, where, f"{path}<cursor>")
        if URL_KEY.search(key) or value.startswith(("/", "http://", "https://")):
            parts = urlsplit(value)
            if URL_KEY.search(key) and any(DIGITS.match(seg) for seg in parts.path.split("/") if seg):
                self.report(where, path, "digit-only path segment in a URL")
            for name, values in parse_qs(parts.query).items():
                for v in values:
                    if CURSOR_KEY.search(name):
                        inner = decode_cursor(v)
                        if inner is not None:
                            self.walk(inner, where, f"{path}?{name}<cursor>")
                    elif ID_KEY.match(name) and DIGITS.match(v):
                        self.report(where, f"{path}?{name}", "internal ID in a query parameter")


def load_allowlist(path: Path) -> list[tuple[str, str]]:
    entries = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            raise ValueError(f"{path}:{n}: allowlist entry '{parts[0]}' has no reason")
        entries.append((parts[0], parts[1]))
    return entries


def documents(path: Path):
    if str(path) == "-":
        text = sys.stdin.read()
        try:
            yield "<stdin>", json.loads(text)
        except ValueError:
            for n, line in enumerate(text.splitlines(), 1):
                if line.strip():
                    yield f"<stdin>:{n}", json.loads(line)
        return
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        for n, line in enumerate(text.splitlines(), 1):
            if line.strip():
                yield f"{path}:{n}", json.loads(line)
    else:
        yield str(path), json.loads(text)


def cursor_of(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")


def self_test() -> int:
    cur = cursor_of({"id": 42, "_pointsToNextItems": True})
    leaks = [
        {"id": 42},
        {"customer_id": "42"},
        {"line_item_ids": [1, 2]},
        {"invoiceId": 7},
        {"data": {"customer": {"id": 9}}},
        {"next_cursor": cur},
        {"next_page_url": f"/invoices?cursor={cur}"},
        {"headers": {"Location": "/invoices/42"}},
        {"links": [{"href": "https://app.example.com/invoices/42"}]},
    ]
    clean = [
        {"id": "V1StGXR8Z5jdHi6BmyT0a"},
        {"chat_id": 123},
        {"invoice_count": 3, "total_cents": 1999},
        {"next_cursor": cursor_of({"created_at": "2026-01-01T00:00:00Z", "public_id": "V1StGXR8Z5jdHi6BmyT0a"})},
        {"is_paid": True, "paid": False},
    ]
    failures = 0
    for doc in leaks:
        s = Scanner([])
        s.walk(doc, "leak")
        if not s.findings:
            print(f"self-test FAIL: leak not caught: {json.dumps(doc)}")
            failures += 1
    for doc in clean:
        s = Scanner([("chat_id", "third-party numeric key")])
        s.walk(doc, "clean")
        if s.findings:
            print(f"self-test FAIL: false positive: {s.findings[0]}")
            failures += 1
    total = len(leaks) + len(clean)
    print(f"self-test: {total - failures}/{total} shapes as expected")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="scan_id_leaks.py",
        description="Scan captured JSON or JSONL payloads for internal record IDs.",
        epilog="Allowlist file: one 'key-or-json-path-glob reason' entry per line; an entry without a reason is an "
        "error. Exit codes: 0 clean, 1 leaks found, 2 usage or input error.",
    )
    ap.add_argument("paths", nargs="*", type=Path, help="JSON or JSONL files, directories to scan recursively, or - for stdin")
    ap.add_argument("--allow-file", type=Path, help="allowlist file")
    ap.add_argument("--self-test", action="store_true", help="feed built-in leak and clean shapes to the scanner")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2
    try:
        allow = load_allowlist(args.allow_file) if args.allow_file else []
    except (OSError, ValueError) as e:
        print(f"scan_id_leaks.py: {e}", file=sys.stderr)
        return 2

    files: list[Path] = []
    for p in args.paths:
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in {".json", ".jsonl"})
        else:
            files.append(p)
    scanner = Scanner(allow)
    for f in files:
        try:
            for where, doc in documents(f):
                scanner.walk(doc, where)
        except (OSError, ValueError) as e:
            print(f"scan_id_leaks.py: cannot read {f}: {e}", file=sys.stderr)
            return 2
    for line in scanner.findings:
        print(line)
    print(f"{len(scanner.findings)} finding(s) in {len(files)} file(s)", file=sys.stderr)
    return 1 if scanner.findings else 0


if __name__ == "__main__":
    sys.exit(main())
