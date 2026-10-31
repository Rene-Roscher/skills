#!/usr/bin/env python3
"""Find internal sequential IDs in captured payloads or in PHP sources.

payload: walks JSON documents (API bodies, Inertia page props, export files,
webhook bodies, broadcast payloads) and reports integer or digit-only values
under keys named id, *_id, *_ids, *Id or *Ids. String values that look like a
pagination cursor (keys ending in "cursor", or a cursor= query parameter in a
URL) are base64url-decoded and walked as well. URLs are checked for *_id query
parameters.

source: scans PHP files for array entries whose key is id/*_id/*_ids and whose
value reads an internal key (->id, ->something_id, pluck('id')), other than
the external ID column (--external-column, default public_id). A line that
must stay is marked with a trailing comment "id-leak: allow [reason]".

Exit codes: 0 no finding (or --report), 1 finding, 2 usage or input error.
Standard library only, no network.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ID_KEY = re.compile(r"^(id|.+_ids?|.*[a-z0-9]Ids?)$")
DIGITS = re.compile(r"^-?\d+$")
CURSOR_KEY = re.compile(r"cursor$", re.I)
URL_KEY = re.compile(r"(location|redirect|url|href|link|self)$", re.I)

PHP_ENTRY = re.compile(
    r"""['"](?P<key>id|[A-Za-z0-9_]+_ids?)['"]\s*=>\s*(?P<value>[^,\]\n]+)"""
)
PHP_PROPERTY = re.compile(r"->([A-Za-z0-9_]+)\b(?!\s*\()")
PHP_PLUCK_ID = re.compile(r"""pluck\(\s*['"]id['"]""")
ALLOW_MARK = re.compile(r"id-leak:\s*allow\s+\S")


def is_internal_value(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        return bool(DIGITS.match(value))
    return False


def decode_cursor(text: str) -> object | None:
    padded = text + "=" * (-len(text) % 4)
    for decoder in (base64.urlsafe_b64decode, base64.b64decode):
        try:
            raw = decoder(padded.encode("ascii"))
            return json.loads(raw.decode("utf-8"))
        except (binascii.Error, ValueError, UnicodeError):
            continue
    return None


class PayloadChecker:
    def __init__(self, allow_keys: set[str]) -> None:
        self.allow_keys = allow_keys
        self.findings: list[str] = []

    def report(self, where: str, path: str, detail: str) -> None:
        self.findings.append(f"{where}: {path or '$'}: {detail}")

    def check_url(self, where: str, path: str, url: str, key: str) -> None:
        parts = urlsplit(url)
        if URL_KEY.search(key):
            for segment in parts.path.split("/"):
                if DIGITS.match(segment):
                    self.report(where, path, f"numeric path segment in {url}")
                    break
        for name, value in parse_qsl(parts.query, keep_blank_values=True):
            if name == "cursor":
                decoded = decode_cursor(value)
                if decoded is not None:
                    self.walk(where, f"{path}<cursor>", decoded)
            elif ID_KEY.match(name) and name not in self.allow_keys and DIGITS.match(value):
                self.report(where, path, f"query parameter {name}={value}")

    def walk(self, where: str, path: str, node: object, key: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                key = str(key)
                child = f"{path}.{key}" if path else key
                if ID_KEY.match(key) and key not in self.allow_keys:
                    values = value if isinstance(value, list) else [value]
                    for v in values:
                        if is_internal_value(v):
                            self.report(where, child, f"internal-looking value {v!r}")
                if isinstance(value, str) and CURSOR_KEY.search(key):
                    decoded = decode_cursor(value)
                    if decoded is not None:
                        self.walk(where, f"{child}<cursor>", decoded)
                self.walk(where, child, value, key)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                self.walk(where, f"{path}[{i}]", item)
        elif isinstance(node, str) and node.startswith(("http://", "https://", "/")):
            self.check_url(where, path, node, key)


def run_payload(args: argparse.Namespace) -> int:
    checker = PayloadChecker(set(args.allow_key or []))
    for name in args.files:
        try:
            text = sys.stdin.read() if name == "-" else Path(name).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {name}: {exc}", file=sys.stderr)
            return 2
        docs: list[object] = []
        try:
            docs.append(json.loads(text))
        except json.JSONDecodeError:
            # JSON Lines: one document per line.
            try:
                docs = [json.loads(line) for line in text.splitlines() if line.strip()]
            except json.JSONDecodeError as exc:
                print(f"{name}: not JSON or JSON Lines: {exc}", file=sys.stderr)
                return 2
        for doc in docs:
            checker.walk(name, "", doc)
    for finding in checker.findings:
        print(finding)
    if checker.findings and not args.report:
        return 1
    return 0


def reads_internal_key(value: str, external: set[str]) -> bool:
    if PHP_PLUCK_ID.search(value):
        return True
    props = PHP_PROPERTY.findall(value)
    if not props:
        return False
    last = props[-1]
    return last == "id" or (last.endswith("_id") and last not in external)


def run_source(args: argparse.Namespace) -> int:
    external = set(args.external_column or ["public_id"])
    findings: list[str] = []
    for root in args.paths:
        base = Path(root)
        if not base.exists():
            print(f"no such path: {root}", file=sys.stderr)
            return 2
        files = [base] if base.is_file() else sorted(base.rglob("*.php"))
        for path in files:
            if "vendor" in path.parts:
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for n, line in enumerate(lines, 1):
                if ALLOW_MARK.search(line):
                    continue
                stripped = line.lstrip()
                if stripped.startswith(("//", "#", "*", "/*")):
                    continue
                for m in PHP_ENTRY.finditer(line):
                    if reads_internal_key(m.group("value"), external):
                        findings.append(f"{path}:{n}: '{m.group('key')}' => {m.group('value').strip()}")
    for finding in findings:
        print(finding)
    if findings and not args.report:
        return 1
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Find internal sequential IDs in captured payloads or PHP sources.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p = sub.add_parser("payload", help="check JSON or JSON Lines files ('-' reads stdin)")
    p.add_argument("files", nargs="+")
    p.add_argument("--allow-key", action="append", metavar="KEY",
                   help="key that may carry an integer, such as a foreign system's chat_id (repeatable)")
    p.add_argument("--report", action="store_true", help="print findings but exit 0")
    p.set_defaults(func=run_payload)

    s = sub.add_parser("source", help="scan PHP files or directories")
    s.add_argument("paths", nargs="+")
    s.add_argument("--external-column", action="append", metavar="NAME",
                   help="column that holds the external ID (default public_id, repeatable)")
    s.add_argument("--report", action="store_true", help="print findings but exit 0")
    s.set_defaults(func=run_source)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
