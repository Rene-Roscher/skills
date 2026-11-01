#!/usr/bin/env python3
"""Scan SQL migration files for statements that block writes or break zero-downtime deploys on PostgreSQL.

Usage:
  pg_lint_migration.py PATH [PATH ...]    files or directories (directories are searched for *.sql)
  pg_lint_migration.py --self-test

Rules (an error exits 1, a warning does not change the exit code):
  M01 error    CREATE INDEX without CONCURRENTLY on a table not created in the same file
  M02 error    ADD CONSTRAINT FOREIGN KEY or CHECK (also ADD FOREIGN KEY, ADD CHECK) without NOT VALID
  M03 error    ALTER COLUMN ... TYPE (most type changes rewrite the table)
  M04 error    ALTER COLUMN ... SET NOT NULL without an earlier valid CHECK (col IS NOT NULL) in the same file
  M05 error    DROP COLUMN without a comment containing the word "contract" on the statement
  M06 error    UPDATE or DELETE without WHERE
  M07 warning  data change (UPDATE/DELETE) in the same file as a table-altering statement
  M08 error    locking statement without an earlier SET lock_timeout in the same file
  M09 error    CREATE INDEX CONCURRENTLY or DROP INDEX CONCURRENTLY inside an explicit BEGIN block

Suppress one finding with a comment on the statement, or on the lines directly above it:
  -- migration-lint: allow M03 varchar(50) to varchar(80), no rewrite, checked in the docs
A reason after the rule ID is required; an allow without a reason is ignored and reported as M00.
M08 is a file-level rule: an allow comment anywhere in the file suppresses it.

The scanner is conservative and works on text: it strips comments and string literals, splits on
semicolons and reads each statement with regular expressions. It does not parse dollar-quoted bodies
(DO blocks, function bodies), so statements inside them are not checked. Python 3.8 or later,
standard library only, no network.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

IDENT = r'(?:"[^"]+"|[A-Za-z_][\w$]*)'
QNAME = rf"({IDENT}(?:\s*\.\s*{IDENT})?)"
ALLOW_RE = re.compile(r"migration-lint:\s*allow\s+(M\d{2})\b(.*)", re.I)


def norm_name(raw):
    last = re.split(r"\s*\.\s*", raw.strip())[-1]
    return last.strip('"').lower()


def split_statements(text):
    """Return statements as dicts: clean (comments removed, strings blanked), line, comments."""
    stmts = []
    clean, comments = [], []
    pending_comments = []
    i, n, line = 0, len(text), 1
    start_line = None
    depth_block = 0

    def flush():
        nonlocal clean, pending_comments, start_line
        body = "".join(clean).strip()
        if body:
            stmts.append({"clean": re.sub(r"\s+", " ", body), "line": start_line or line,
                          "comments": pending_comments})
            pending_comments = []
        clean = []
        start_line = None

    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            clean.append(c)
            i += 1
        elif text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            pending_comments.append((line, text[i + 2:j]))
            i = j
        elif text.startswith("/*", i):
            depth_block, j, startl = 1, i + 2, line
            while j < n and depth_block:
                if text.startswith("/*", j):
                    depth_block += 1
                    j += 2
                elif text.startswith("*/", j):
                    depth_block -= 1
                    j += 2
                else:
                    if text[j] == "\n":
                        line += 1
                    j += 1
            pending_comments.append((startl, text[i + 2:j - 2]))
            i = j
        else:
            if start_line is None and not c.isspace():
                start_line = line
            if c == "'":
                escape = i > 0 and text[i - 1] in "eE" and (i < 2 or not re.match(r"\w", text[i - 2]))
                j = i + 1
                while j < n:
                    if escape and text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == "'":
                        if text.startswith("''", j):
                            j += 2
                            continue
                        break
                    if text[j] == "\n":
                        line += 1
                    j += 1
                clean.append("''")
                i = j + 1
            elif c == '"':
                j = text.find('"', i + 1)
                j = n - 1 if j == -1 else j
                clean.append(text[i:j + 1])
                i = j + 1
            elif c == "$":
                m = re.match(r"\$([A-Za-z_]\w*)?\$", text[i:])
                if m:
                    tag = m.group(0)
                    j = text.find(tag, i + len(tag))
                    j = n if j == -1 else j + len(tag)
                    line += text[i:j].count("\n")
                    clean.append("$$")
                    i = j
                else:
                    clean.append(c)
                    i += 1
            elif c == ";":
                flush()
                i += 1
            elif c == "\\" and (i == 0 or text[i - 1] == "\n"):
                j = text.find("\n", i)
                i = n if j == -1 else j
            else:
                clean.append(c)
                i += 1
    flush()
    return stmts


def split_actions(rest):
    """Split the text after the table name of ALTER TABLE on top-level commas."""
    parts, depth, cur = [], 0, []
    for ch in rest:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


def lint_text(text):
    """Return a list of (line, rule, severity, message)."""
    stmts = split_statements(text)
    findings = []
    created = set()
    notnull_checks = {}   # (table, column) -> constraint name, only while valid-or-pending
    validated = set()     # (table, constraint name)
    lock_timeout_seen = False
    in_begin = False
    has_data_change = False
    first_alter_line = None
    file_allows = set()
    allow_errors = []

    def allows_for(stmt):
        found = set()
        for ln, body in stmt["comments"]:
            m = ALLOW_RE.search(body)
            if m:
                if m.group(2).strip():
                    found.add(m.group(1).upper())
                else:
                    allow_errors.append((ln, m.group(1).upper()))
        return found

    for stmt in stmts:
        for ln, body in stmt["comments"]:
            m = ALLOW_RE.search(body)
            if m and m.group(2).strip():
                file_allows.add(m.group(1).upper())

    def add(stmt, rule, sev, msg, allows):
        if rule in allows:
            return
        if rule == "M08":
            if any(f[1] == "M08" for f in findings):
                return
        findings.append((stmt["line"], rule, sev, msg))

    for stmt in stmts:
        s = stmt["clean"]
        allows = allows_for(stmt)
        comment_text = " ".join(b for _, b in stmt["comments"]).lower()

        if re.match(r"(BEGIN|START\s+TRANSACTION)\b", s, re.I):
            in_begin = True
            continue
        if re.match(r"(COMMIT|END|ROLLBACK)\b", s, re.I):
            in_begin = False
            continue

        if re.search(r"\bSET\s+(?:LOCAL\s+|SESSION\s+)?lock_timeout\b", s, re.I):
            lock_timeout_seen = True

        m = re.match(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{QNAME}", s, re.I)
        if m:
            created.add(norm_name(m.group(1)))
            continue

        m = re.match(rf"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?(?:{IDENT}\s+)?ON\s+(?:ONLY\s+)?{QNAME}", s, re.I)
        if m:
            table = norm_name(m.group(2))
            if m.group(1):
                if in_begin:
                    add(stmt, "M09", "error", "CREATE INDEX CONCURRENTLY cannot run inside a transaction block", allows)
            elif table not in created:
                add(stmt, "M01", "error", f"CREATE INDEX on existing table '{table}' without CONCURRENTLY blocks writes; use CREATE INDEX CONCURRENTLY outside a transaction", allows)
                if not lock_timeout_seen:
                    add(stmt, "M08", "error", "locking statement before any SET lock_timeout", allows | file_allows)
            continue

        m = re.match(r"DROP\s+INDEX\s+(CONCURRENTLY\s+)?", s, re.I)
        if m:
            if m.group(1):
                if in_begin:
                    add(stmt, "M09", "error", "DROP INDEX CONCURRENTLY cannot run inside a transaction block", allows)
            elif not lock_timeout_seen:
                add(stmt, "M08", "error", "locking statement before any SET lock_timeout", allows | file_allows)
            continue

        if re.match(r"DROP\s+TABLE\b", s, re.I) and not lock_timeout_seen:
            add(stmt, "M08", "error", "locking statement before any SET lock_timeout", allows | file_allows)

        m = re.match(rf"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?{QNAME}\s*(.*)$", s, re.I)
        if m:
            table = norm_name(m.group(1))
            if table in created:
                continue
            if first_alter_line is None:
                first_alter_line = stmt["line"]
            if not lock_timeout_seen:
                add(stmt, "M08", "error", "locking statement before any SET lock_timeout", allows | file_allows)
            for action in split_actions(m.group(2)):
                lint_action(stmt, table, action, comment_text, allows, notnull_checks, validated, add)
            continue

        if re.match(r"UPDATE\s+", s, re.I) or re.match(r"DELETE\s+FROM\s+", s, re.I):
            has_data_change = True
            if not re.search(r"\bWHERE\b", s, re.I):
                add(stmt, "M06", "error", "UPDATE or DELETE without WHERE changes every row; batch it with a WHERE on a key range", allows)

    if has_data_change and first_alter_line is not None:
        if "M07" not in file_allows:
            findings.append((first_alter_line, "M07", "warning",
                             "data change and ALTER TABLE in one file usually share one transaction; split the backfill into its own step"))
    for ln, rule in allow_errors:
        findings.append((ln, "M00", "error", f"allow comment for {rule} has no reason; it is ignored"))
    findings.sort(key=lambda f: (f[0], f[1]))
    return findings


def lint_action(stmt, table, action, comment_text, allows, notnull_checks, validated, add):
    a = action
    not_valid = re.search(r"\bNOT\s+VALID\b", a, re.I) is not None

    m = re.match(rf"ADD\s+(?:CONSTRAINT\s+({IDENT})\s+)?(FOREIGN\s+KEY|CHECK)\b(.*)", a, re.I)
    if m:
        cname = (m.group(1) or "").strip('"').lower()
        kind = re.sub(r"\s+", " ", m.group(2).upper())
        if not not_valid:
            add(stmt, "M02", "error", f"ADD {kind} without NOT VALID scans the table under a lock; add NOT VALID, then VALIDATE CONSTRAINT in a later statement", allows)
        if kind == "CHECK":
            cm = re.match(rf"\(\s*\(?\s*({IDENT})\s+IS\s+NOT\s+NULL\s*\)?\s*\)", m.group(3).strip(), re.I)
            if cm:
                col = cm.group(1).strip('"').lower()
                notnull_checks[(table, col)] = cname
                if not not_valid:
                    validated.add((table, cname))
        return

    m = re.match(rf"VALIDATE\s+CONSTRAINT\s+({IDENT})", a, re.I)
    if m:
        validated.add((table, m.group(1).strip('"').lower()))
        return

    if re.match(rf"ALTER\s+(?:COLUMN\s+)?{IDENT}\s+(?:SET\s+DATA\s+)?TYPE\b", a, re.I):
        add(stmt, "M03", "error", "ALTER COLUMN TYPE usually rewrites the table and its indexes under ACCESS EXCLUSIVE; use expand and contract with a new column", allows)
        return

    m = re.match(rf"ALTER\s+(?:COLUMN\s+)?({IDENT})\s+SET\s+NOT\s+NULL\b", a, re.I)
    if m:
        col = m.group(1).strip('"').lower()
        cname = notnull_checks.get((table, col))
        if cname is None or (table, cname) not in validated:
            add(stmt, "M04", "error", f"SET NOT NULL on '{table}.{col}' scans the table under ACCESS EXCLUSIVE; first ADD CONSTRAINT CHECK ({col} IS NOT NULL) NOT VALID and VALIDATE it in this file", allows)
        return

    if re.match(r"DROP\b(?!\s+CONSTRAINT\b)", a, re.I):
        if "contract" not in comment_text:
            add(stmt, "M05", "error", "DROP COLUMN needs a comment containing 'contract' that names the release which stopped using the column", allows)


# --------------------------------------------------------------------------- self test

GOOD = {
    "create-table-and-index": """
        CREATE TABLE booking (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, room_id bigint NOT NULL);
        CREATE INDEX booking_room_id_idx ON booking (room_id);
    """,
    "concurrent-index": """
        -- no BEGIN here: CONCURRENTLY cannot run in a transaction block
        CREATE INDEX CONCURRENTLY IF NOT EXISTS booking_room_id_idx ON booking (room_id);
    """,
    "not-valid-then-validate": """
        SET lock_timeout = '3s';
        ALTER TABLE booking ADD CONSTRAINT booking_room_fk FOREIGN KEY (room_id) REFERENCES room (id) NOT VALID;
        ALTER TABLE booking VALIDATE CONSTRAINT booking_room_fk;
    """,
    "not-null-via-check": """
        SET lock_timeout = '3s';
        ALTER TABLE invoice ADD CONSTRAINT invoice_paid_at_nn CHECK (paid_at IS NOT NULL) NOT VALID;
        ALTER TABLE invoice VALIDATE CONSTRAINT invoice_paid_at_nn;
        ALTER TABLE invoice ALTER COLUMN paid_at SET NOT NULL;
        ALTER TABLE invoice DROP CONSTRAINT invoice_paid_at_nn;
    """,
    "add-column-with-default": """
        SET lock_timeout = '3s';
        ALTER TABLE invoice ADD COLUMN currency text NOT NULL DEFAULT 'EUR';
    """,
    "drop-column-contract": """
        SET lock_timeout = '3s';
        -- contract: release 2026.11 stopped reading legacy_note
        ALTER TABLE invoice DROP COLUMN legacy_note;
    """,
    "batched-update-with-where": """
        UPDATE invoice SET currency = 'EUR' WHERE id BETWEEN 1 AND 10000 AND currency IS NULL;
    """,
    "allow-with-reason": """
        SET lock_timeout = '3s';
        -- migration-lint: allow M03 varchar(50) to varchar(80) needs no rewrite, see ALTER TABLE notes
        ALTER TABLE invoice ALTER COLUMN number TYPE varchar(80);
    """,
    "strings-and-dollar-quotes-ignored": """
        INSERT INTO note (body) VALUES ('UPDATE booking SET x = 1; DELETE FROM booking');
        DO $body$ BEGIN PERFORM 1; END $body$;
    """,
}

BAD = {
    "create-index-plain": ("CREATE INDEX booking_room_id_idx ON booking (room_id);", {"M01", "M08"}),
    "fk-without-not-valid": ("SET lock_timeout='3s';\nALTER TABLE booking ADD CONSTRAINT f FOREIGN KEY (room_id) REFERENCES room (id);", {"M02"}),
    "check-without-not-valid": ("SET lock_timeout='3s';\nALTER TABLE booking ADD CONSTRAINT c CHECK (price >= 0);", {"M02"}),
    "unnamed-fk": ("SET lock_timeout='3s';\nALTER TABLE booking ADD FOREIGN KEY (room_id) REFERENCES room (id);", {"M02"}),
    "alter-type": ("SET lock_timeout='3s';\nALTER TABLE invoice ALTER COLUMN total TYPE numeric(12,2);", {"M03"}),
    "set-not-null-bare": ("SET lock_timeout='3s';\nALTER TABLE invoice ALTER COLUMN paid_at SET NOT NULL;", {"M04"}),
    "set-not-null-unvalidated-check": ("SET lock_timeout='3s';\nALTER TABLE invoice ADD CONSTRAINT nn CHECK (paid_at IS NOT NULL) NOT VALID;\nALTER TABLE invoice ALTER COLUMN paid_at SET NOT NULL;", {"M04"}),
    "drop-column-no-comment": ("SET lock_timeout='3s';\nALTER TABLE invoice DROP COLUMN legacy_note;", {"M05"}),
    "update-no-where": ("UPDATE invoice SET currency = 'EUR';", {"M06"}),
    "delete-no-where": ("DELETE FROM invoice;", {"M06"}),
    "no-lock-timeout": ("ALTER TABLE invoice ADD COLUMN note text;", {"M08"}),
    "lock-timeout-after-statement": ("ALTER TABLE invoice ADD COLUMN note text;\nSET lock_timeout='3s';", {"M08"}),
    "concurrently-in-begin": ("BEGIN;\nCREATE INDEX CONCURRENTLY i ON booking (room_id);\nCOMMIT;", {"M09"}),
    "allow-without-reason": ("SET lock_timeout='3s';\n-- migration-lint: allow M03\nALTER TABLE invoice ALTER COLUMN total TYPE bigint;", {"M00", "M03"}),
    "multi-action-one-bad": ("SET lock_timeout='3s';\nALTER TABLE booking ADD COLUMN a int, ADD CONSTRAINT c CHECK (a > 0);", {"M02"}),
}


def self_test():
    failures = []
    for name, sql in GOOD.items():
        found = {f[1] for f in lint_text(sql) if f[2] == "error"}
        if found:
            failures.append(f"good case '{name}' reported {sorted(found)}")
    for name, (sql, expected) in BAD.items():
        found = {f[1] for f in lint_text(sql)}
        if not expected <= found:
            failures.append(f"bad case '{name}' expected {sorted(expected)}, got {sorted(found)}")
    warn = {f[1] for f in lint_text("SET lock_timeout='3s';\nALTER TABLE a ADD COLUMN b int;\nUPDATE a SET b = 1 WHERE id < 10;")}
    if "M07" not in warn:
        failures.append("M07 warning not reported for DDL plus data change")
    ok = {f[1] for f in lint_text("CREATE TABLE a (id int);\nALTER TABLE a ADD CONSTRAINT c CHECK (id > 0);\nCREATE INDEX ON a (id);")}
    if ok:
        failures.append(f"table created in the same file must be exempt, got {sorted(ok)}")
    if failures:
        for f in failures:
            print("FAIL " + f)
        return 1
    print(f"self-test passed: {len(GOOD)} good cases, {len(BAD)} bad cases, 2 extra checks")
    return 0


def collect(paths):
    files = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.sql")))
        else:
            files.append(path)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint SQL migrations for lock-heavy statements on PostgreSQL.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2
    files = collect(args.paths)
    if not files:
        print("no .sql files found", file=sys.stderr)
        return 2
    errors = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"{f}: cannot read: {e}", file=sys.stderr)
            return 2
        for line, rule, sev, msg in lint_text(text):
            print(f"{f}:{line}: {sev} [{rule}] {msg}")
            if sev == "error":
                errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
