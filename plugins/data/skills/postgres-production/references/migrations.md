# Migrations without downtime

## Contents

- Lock levels that matter
- The lock queue and `lock_timeout`
- Recipes
- Version map
- Linter rules and false positives

All statements below were checked against the PostgreSQL manual for the current major (18) on 2026-11-01 unless a
version is named. Where the text says "ran", the statement was executed on PostgreSQL 17.10 on 2026-11-01.

## Lock levels that matter

Source: https://www.postgresql.org/docs/current/explicit-locking.html (verified 2026-11-01).

- `ACCESS EXCLUSIVE` conflicts with every other mode, plain `SELECT` included. Most `ALTER TABLE` forms take it,
  as the manual says: "An ACCESS EXCLUSIVE lock is acquired unless explicitly noted." With several subcommands,
  the strictest one applies.
- `ADD FOREIGN KEY` takes `SHARE ROW EXCLUSIVE` on the table and on the referenced table.
- `VALIDATE CONSTRAINT` takes `SHARE UPDATE EXCLUSIVE` (plus `ROW SHARE` on the referenced table for a foreign
  key), so reads and writes continue.
- A plain `CREATE INDEX` locks out writes but not reads (CREATE INDEX page). `CREATE INDEX CONCURRENTLY` allows writes.
- Locks are held until the end of the transaction. That is why DDL plus a long data change in one transaction is
  the worst combination.

Source for the `ALTER TABLE` levels: https://www.postgresql.org/docs/current/sql-altertable.html (verified 2026-11-01).

## The lock queue and `lock_timeout`

A statement that needs ACCESS EXCLUSIVE waits for every open transaction that touched the table. While it waits,
new queries on the table queue behind it. The outage is the wait, not the DDL. Ran: session A read the table in an
open transaction, session B issued `ALTER TABLE q ADD COLUMN x int`, and a `SELECT count(*)` in session C waited
about 4 seconds, until A finished. With `SET lock_timeout = '500ms'` in B, B failed with "canceling statement due to
lock timeout" and C ran at once.

Source: https://www.postgresql.org/docs/current/runtime-config-client.html (verified 2026-11-01): `lock_timeout`
aborts a statement that waits longer than the limit for a lock, applies per lock acquisition, and the manual advises
against setting it in `postgresql.conf` because it would affect all sessions. Set it per migration session. It is
pointless to set `lock_timeout` equal to or larger than a non-zero `statement_timeout`, because the statement
timeout fires first (same page).

Pattern for a lock-taking step:

```sql
SET lock_timeout = '3s';
ALTER TABLE invoice ADD COLUMN currency text NOT NULL DEFAULT 'EUR';
```

The runner retries the file when it fails with a lock timeout, with a pause and a limit. Keep each step small so a
retry is cheap. `SET LOCAL` inside the migration's own transaction limits the setting to that transaction
(https://www.postgresql.org/docs/current/sql-set.html, verified 2026-11-01).

## Recipes

### Index on a live table

```sql
-- no BEGIN: CONCURRENTLY cannot run in a transaction block
CREATE INDEX CONCURRENTLY IF NOT EXISTS booking_room_id_idx ON booking (room_id);
```

- Run it as its own migration file. A runner that wraps files in a transaction needs that wrapper off for this
  file.
- It does two table scans and waits for older transactions, so it takes longer and loads I/O. Only one concurrent
  build can run on a table at a time. Concurrent builds on a partitioned table are not supported; build each
  partition's index concurrently, then create the parent index (a metadata-only step).
- A unique concurrent build enforces uniqueness against other transactions before it finishes; a failed one leaves
  an invalid index that keeps enforcing uniqueness.
- Check `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;` after every run. Drop the leftover with
  `DROP INDEX CONCURRENTLY` (one index per command, no `CASCADE`, so an index behind a primary key or unique
  constraint cannot be dropped this way) and rebuild.
- `REINDEX ... CONCURRENTLY` rebuilds a bloated or invalid index without the write lock. It exists from PostgreSQL
  12; the 11 manual says REINDEX does not build concurrently.

Sources: https://www.postgresql.org/docs/current/sql-createindex.html,
https://www.postgresql.org/docs/current/sql-dropindex.html, https://www.postgresql.org/docs/current/sql-reindex.html,
https://www.postgresql.org/docs/12/sql-reindex.html, https://www.postgresql.org/docs/11/sql-reindex.html
(verified 2026-11-01).

### Foreign key or CHECK on an existing table

```sql
SET lock_timeout = '3s';
ALTER TABLE booking
  ADD CONSTRAINT booking_room_fk FOREIGN KEY (room_id) REFERENCES room (id) NOT VALID;
-- separate statement, ideally a separate migration
ALTER TABLE booking VALIDATE CONSTRAINT booking_room_fk;
```

`NOT VALID` skips the scan. New writes are checked at once; old rows are checked by `VALIDATE`. If old rows are
known to violate the rule, the constraint can be in place while you fix them. Also index the referencing column
(`CREATE INDEX CONCURRENTLY`).

Source: https://www.postgresql.org/docs/current/sql-altertable.html (verified 2026-11-01).

### NOT NULL on an existing column

```sql
SET lock_timeout = '3s';
ALTER TABLE invoice ADD CONSTRAINT invoice_paid_at_nn CHECK (paid_at IS NOT NULL) NOT VALID;
ALTER TABLE invoice VALIDATE CONSTRAINT invoice_paid_at_nn;
ALTER TABLE invoice ALTER COLUMN paid_at SET NOT NULL;  -- skips the scan: a valid CHECK proves it
ALTER TABLE invoice DROP CONSTRAINT invoice_paid_at_nn;
```

Ran: without the CHECK, `SET NOT NULL` logged `verifying table "n"` (a scan); with the validated CHECK it logged
"existing constraints on column "n.v" are sufficient to prove that it does not contain nulls". The manual states
the shortcut for PostgreSQL 12 and later, not for 11. From PostgreSQL 18, `ALTER TABLE` can also set `NOT VALID`
on a NOT NULL constraint directly (release notes 18). Backfill the NULL rows in batches before `VALIDATE`.

Sources: https://www.postgresql.org/docs/current/sql-altertable.html, https://www.postgresql.org/docs/12/sql-altertable.html,
https://www.postgresql.org/docs/11/sql-altertable.html, https://www.postgresql.org/docs/release/18.0/
(verified 2026-11-01).

### New column with a default

From PostgreSQL 11 a constant (non-volatile) default is stored in the catalog and needs no rewrite. A volatile
default, a stored generated column, an identity column, or a domain type with constraints rewrites the whole table
and its indexes. A virtual generated column (PostgreSQL 18) never rewrites. Ran: the table's file node stayed the
same after `ADD COLUMN flag boolean NOT NULL DEFAULT false` and changed after `ADD COLUMN created timestamptz NOT
NULL DEFAULT clock_timestamp()`. For a volatile default: add the column nullable, backfill in batches, then set
the default and the NOT NULL via the CHECK route.

Sources: https://www.postgresql.org/docs/current/sql-altertable.html, https://www.postgresql.org/docs/release/11.0/,
https://www.postgresql.org/docs/10/sql-altertable.html (verified 2026-11-01).

### Type change or rename: expand and contract

1. Expand: add the new column or table; deploy code that writes both.
2. Backfill in batches (below).
3. Switch reads to the new column; deploy.
4. Contract: stop writing the old one; in a later release drop it with a comment containing `contract`.

Renames follow the same path, because running instances still use the old name during a rolling deploy.
A type change is only metadata-only when the `USING` expression does not change the contents and the types are
binary coercible, and indexes may still rebuild (https://www.postgresql.org/docs/current/sql-altertable.html,
verified 2026-11-01). Treat that as a case for an inline allow with the reason written down.

### Backfill in batches

```sql
-- one batch; the runner loops until it updates 0 rows, one commit per batch
UPDATE invoice SET currency = 'EUR'
WHERE id IN (
  SELECT id FROM invoice WHERE currency IS NULL ORDER BY id LIMIT 5000
);
```

- Keep batches small enough that each commits in well under a second, and pause between them so replicas and
  autovacuum keep up.
- Each batch needs an index or key range that finds its rows without scanning the table again.
- Keep this out of the transaction that holds DDL, and keep the transaction short: an old open transaction stops
  vacuum from removing dead rows (https://www.postgresql.org/docs/current/routine-vacuuming.html, verified
  2026-11-01).

## Version map

| Behaviour | Holds from | Source (verified 2026-11-01) |
|---|---|---|
| `CREATE INDEX CONCURRENTLY` | 8.2 (absent from the 8.1 page) | https://www.postgresql.org/docs/8.2/sql-createindex.html |
| Constant default without table rewrite | 11 | https://www.postgresql.org/docs/release/11.0/ |
| `REINDEX CONCURRENTLY` | 12 | https://www.postgresql.org/docs/12/sql-reindex.html |
| `SET NOT NULL` skips its scan with a valid CHECK | 12 | https://www.postgresql.org/docs/12/sql-altertable.html |
| `MERGE` | 15 (the 14 page does not exist) | https://www.postgresql.org/docs/release/15.0/ |
| `UNIQUE NULLS NOT DISTINCT` | 15 | https://www.postgresql.org/docs/release/15.0/ |
| `pg_stat_user_indexes.last_idx_scan` | 16 (absent from the 15 page) | https://www.postgresql.org/docs/16/monitoring-stats.html |
| `uuidv7()`, `NOT VALID` on NOT NULL, `BUFFERS` default with `ANALYZE` | 18 | https://www.postgresql.org/docs/release/18.0/ |

## Linter rules and false positives

`scripts/pg_lint_migration.py` reads `.sql` files. It strips comments and string literals, splits on semicolons and
matches statements with regular expressions. It does not read the inside of dollar-quoted blocks (`DO`, function
bodies) and does not know which tables are large.

| Rule | Reports |
|---|---|
| M01 | `CREATE INDEX` without `CONCURRENTLY` on a table not created in the same file |
| M02 | `ADD CONSTRAINT` or `ADD` of a foreign key or CHECK without `NOT VALID` |
| M03 | `ALTER COLUMN ... TYPE` |
| M04 | `SET NOT NULL` without an earlier valid `CHECK (col IS NOT NULL)` in the same file |
| M05 | `DROP COLUMN` without a comment containing `contract` |
| M06 | `UPDATE` or `DELETE` without `WHERE` |
| M07 | warning: a data change and an `ALTER TABLE` in one file |
| M08 | a locking statement before any `SET lock_timeout` in the file (reported once per file) |
| M09 | `CREATE INDEX CONCURRENTLY` or `DROP INDEX CONCURRENTLY` after `BEGIN` |

A table created in the same file is exempt from M01 to M05, because nobody uses it yet. Typical false positives:
a tiny lookup table (M01, M02), a type change with no rewrite (M03), a `DELETE` inside a script that is not a
migration. Suppress one finding with a comment on the statement or the lines above it:

```sql
-- migration-lint: allow M03 varchar(50) to varchar(80) needs no rewrite, checked in the ALTER TABLE notes
ALTER TABLE invoice ALTER COLUMN number TYPE varchar(80);
```

An allow without a reason is ignored and reported as M00. M08 is file-level: one allow anywhere in the file
suppresses it. The linter finds only what it can match as text; a clean run is not proof the migration is safe.
