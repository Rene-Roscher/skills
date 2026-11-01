---
name: postgres-production
description: "Decides how application code and migrations talk to PostgreSQL in production: parameterised queries, keyset pagination, index design, zero-downtime DDL with lock_timeout and NOT VALID, batched backfills, savepoints and retries, pooler limits, timestamptz, EXPLAIN. Use when writing PostgreSQL queries, indexes or migrations. Not for ORM syntax, ClickHouse, Redis or backups."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# PostgreSQL in production

This skill decides what application code and schema changes must do to be safe on a live PostgreSQL database:
how to query and paginate, which indexes to build and how, how to change a table while traffic runs, what a
transaction does after an error, and what a connection pooler takes away. Syntax stays with the PostgreSQL
manual; this skill keeps the decisions, the invariants and the traps. The failure it prevents: a change that is
correct on a small test database and takes the site down, or silently loses data, on the real one.

Version baseline: PostgreSQL 18 is the current major release (18.6); 14 reaches end of life on 2026-11-12. Rules
that depend on a version say from which major they hold. Source: https://www.postgresql.org/support/versioning/
(verified 2026-11-01).

## Applies when / does not apply

- Applies: you write or review SQL or a repository layer that targets PostgreSQL; you add an index, a constraint
  or a column; you plan a migration, a backfill or a type change; a PostgreSQL-only error appears ("current
  transaction is aborted", serialization failure, lock wait, prepared statement does not exist); you put a pooler
  in front of the database; you read an `EXPLAIN` plan.
- Does not apply: ORM API syntax with no PostgreSQL behaviour behind it (for example how a framework spells
  `Schema::table`); schema design for ClickHouse or another engine; Redis or application caching; backups,
  replication and failover (`high-availability`); key conventions for public IDs (`dual-key-identifiers`).

## Rules

### Queries

- [invariant] Send values as bind parameters, never by string concatenation. Identifiers (table, column, sort
  direction) cannot be bound: map them from user input through a fixed allow-list. Why: concatenation turns data
  into code. Test: send `x' OR '1'='1` as a search term; the query returns no rows and the text is stored or
  matched literally. Source: https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html,
  https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html (verified 2026-11-01).
- [invariant] Every `LIMIT`, page and "first" or "latest" query has an `ORDER BY` that ends in a unique column.
  Why: without it the row order is unspecified and different `LIMIT` values can give inconsistent subsets. Test:
  insert 100 rows with the same sort value, fetch pages of 10 with `ORDER BY created_at` only; rows repeat or are
  missing across pages; adding `, id` fixes it. Source: https://www.postgresql.org/docs/current/queries-limit.html
  (verified 2026-11-01).
- [default] Paginate large or growing lists with keyset pagination (`WHERE (created_at, id) < ($1, $2) ORDER BY
  created_at DESC, id DESC LIMIT n`), not `OFFSET`. Trade-off: no jump to page N, and the sort key needs an index.
  Deviate only with an ADR that names this trade-off, for example an admin grid under a few thousand rows. Source:
  https://www.postgresql.org/docs/current/queries-limit.html ("rows skipped by an OFFSET clause still have to be
  computed"), https://www.postgresql.org/docs/current/functions-comparisons.html (row comparison is
  left-to-right) (verified 2026-11-01).
- [default] Load related rows in one batched query (`WHERE parent_id = ANY($1)` or a join), not one query per
  parent. Trade-off: a more complex repository method. Deviate only with an ADR that names this trade-off. Source:
  none; design judgment. Test: a list endpoint with 50 rows issues a constant number of statements, visible as a
  flat `calls` count in `pg_stat_statements`.
- [default] Treat `count(*)` on a large table as a scan. Show "more results" from a `LIMIT n+1` fetch, cap the
  count, or use a stored or estimated figure. Trade-off: the count is approximate or absent. Deviate only with an
  ADR that names this trade-off. Source: https://wiki.postgresql.org/wiki/Slow_Counting (verified 2026-11-01).
- [invariant] Use `NOT EXISTS`, not `NOT IN (subquery)`, when the subquery column can be NULL. Why: one NULL makes
  `NOT IN` return no rows. Test: `SELECT 1 WHERE 1 NOT IN (SELECT y FROM (VALUES (2),(NULL)) v(y))` returns zero
  rows; the `NOT EXISTS` form returns one (run on PostgreSQL 17.10, 2026-11-01). Source:
  https://wiki.postgresql.org/wiki/Don%27t_Do_This (verified 2026-11-01).

### Indexes

- [default] In a multicolumn btree index, put equality columns first, then the range or sort column. Trade-off:
  the index serves fewer query shapes than one per shape. Deviate only with an ADR that names this trade-off.
  Source: https://www.postgresql.org/docs/current/indexes-multicolumn.html (verified 2026-11-01).
- [invariant] Build an index on a table that takes writes with `CREATE INDEX CONCURRENTLY`, outside a
  transaction block, and check `pg_index.indisvalid` after any failure. Why: a plain build locks out writes until
  it finishes; a failed concurrent build leaves an invalid index that still costs writes. Test: `BEGIN; CREATE
  INDEX CONCURRENTLY ...;` fails with "cannot run inside a transaction block"; after a failed build
  `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid` lists the leftover, which you drop with `DROP
  INDEX CONCURRENTLY` and retry. Source: https://www.postgresql.org/docs/current/sql-createindex.html,
  https://www.postgresql.org/docs/current/catalog-pg-index.html (verified 2026-11-01). Holds since PostgreSQL 8.2,
  where the option first appears in the manual (verified 2026-11-01 against the 8.1 and 8.2 pages).
- [default] Index the referencing column of every foreign key. Trade-off: one more index to maintain on writes.
  Deviate only with an ADR that names this trade-off, for example a child table that is never joined and rarely
  loses parent rows. Source: https://www.postgresql.org/docs/current/ddl-constraints.html ("the declaration of a
  foreign key constraint does not automatically create an index on the referencing columns") (verified 2026-11-01).
- [default] Use a partial index when queries filter on a small, stable subset (`WHERE deleted_at IS NULL`), and an
  `INCLUDE` column for an index-only scan only on a hot query. Trade-off: the planner uses a partial index only
  when the query predicate implies its condition, and covering columns grow the index. Deviate only with an ADR
  that names this trade-off. Source: https://www.postgresql.org/docs/current/indexes-partial.html,
  https://www.postgresql.org/docs/current/indexes-index-only-scans.html (verified 2026-11-01).
- [default] Drop an index only on evidence: `idx_scan = 0` in `pg_stat_user_indexes` over a full business cycle on
  every server that serves reads, or an exact duplicate found by comparing key columns, operator classes and
  predicate. Trade-off: waiting costs write overhead and disk. Deviate only with an ADR that names this
  trade-off. Source: https://www.postgresql.org/docs/current/monitoring-stats.html (counters reset after an
  unclean shutdown, a base backup or point-in-time recovery; `last_idx_scan` exists from PostgreSQL 16)
  (verified 2026-11-01).

### Migrations

- [invariant] A migration that needs a strong table lock sets `lock_timeout` first (for example `SET lock_timeout
  = '3s'`) and is retried on timeout. Why: `ALTER TABLE` takes ACCESS EXCLUSIVE unless noted, which conflicts with
  every mode including plain reads, and it queues behind any open transaction; every later query then queues
  behind it. Test: session A holds an open transaction that read the table, session B runs `ALTER TABLE ... ADD
  COLUMN`, session C runs `SELECT count(*)`; C waits as long as A stays open (4 s in a run on PostgreSQL 17.10,
  2026-11-01). With `SET lock_timeout = '500ms'` in B, B fails with "canceling statement due to lock timeout" and C
  is not held up. Source: https://www.postgresql.org/docs/current/explicit-locking.html,
  https://www.postgresql.org/docs/current/runtime-config-client.html (verified 2026-11-01).
- [invariant] Add a foreign key or CHECK constraint to an existing table as `NOT VALID`, then run `VALIDATE
  CONSTRAINT` as a separate statement. Why: the plain form scans the table while writes are locked out;
  validation takes only SHARE UPDATE EXCLUSIVE (plus ROW SHARE on the referenced table for a foreign key). Test:
  the linter reports M02 on `ADD CONSTRAINT ... FOREIGN KEY` without `NOT VALID`; the fixed file contains both
  statements. Source: https://www.postgresql.org/docs/current/sql-altertable.html (verified 2026-11-01).
- [invariant] Make an existing column NOT NULL in three steps: `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT
  VALID`, `VALIDATE CONSTRAINT`, then `SET NOT NULL`, which skips its own scan because a valid CHECK proves it.
  Why: a bare `SET NOT NULL` scans under ACCESS EXCLUSIVE. Test: with the valid CHECK in place, `SET NOT NULL`
  logs "existing constraints on column are sufficient to prove that it does not contain nulls" at `DEBUG1`
  (PostgreSQL 17.10, 2026-11-01). Holds from PostgreSQL 12 (the 11 manual has no such sentence); from 18 a
  not-null constraint can itself be added `NOT VALID`. Source:
  https://www.postgresql.org/docs/current/sql-altertable.html, https://www.postgresql.org/docs/12/sql-altertable.html,
  https://www.postgresql.org/docs/release/18.0/ (verified 2026-11-01).
- [invariant] Never change a column type in place on a large table. Expand and contract: add the new column,
  write both, backfill in batches, switch reads, stop writing the old column, drop it in a later release. Why:
  `ALTER COLUMN TYPE` normally rewrites the table and its indexes under ACCESS EXCLUSIVE; the rewriting forms are
  not MVCC-safe. Test: the linter reports M03; the plan has separate expand and contract migrations. Source:
  https://www.postgresql.org/docs/current/sql-altertable.html (verified 2026-11-01).
- [default] Add a column with a constant default in one statement. Use a separate backfill when the default is
  volatile (`clock_timestamp()`), the column is an identity or stored generated column, or its domain has
  constraints, because those rewrite the table. Trade-off: on versions before 11 every default rewrites, so the
  one-statement form is unsafe there. Deviate only with an ADR that names this trade-off. Source:
  https://www.postgresql.org/docs/current/sql-altertable.html, https://www.postgresql.org/docs/release/11.0/,
  https://www.postgresql.org/docs/10/sql-altertable.html (verified 2026-11-01). Test: `pg_relation_filenode`
  stays the same after `ADD COLUMN flag boolean NOT NULL DEFAULT false` and changes after `ADD COLUMN c
  timestamptz NOT NULL DEFAULT clock_timestamp()` (PostgreSQL 17.10, 2026-11-01).
- [invariant] Run a backfill as its own step, in batches by key range, one commit per batch, each with a `WHERE`.
  Never put DDL and a large data change in the same transaction. Why: locks are held until the transaction ends,
  so the table lock from the `ALTER` lives as long as the `UPDATE`; one huge update also creates dead rows in one
  go. Test: the linter reports M06 for an `UPDATE` without `WHERE` and warns M07 when DDL and a data change share
  a file; the backfill log shows many commits, not one. Source:
  https://www.postgresql.org/docs/current/explicit-locking.html ("a lock is normally held until the end of the
  transaction") (verified 2026-11-01).
- [invariant] Drop a column or table only in a later release than the one that stopped using it, and mark the
  statement with a `contract` comment. Why: running application instances still select the column during a
  rolling deploy. Test: the linter reports M05 for a `DROP COLUMN` without the comment. Source: none; design
  judgment (expand and contract). `DROP COLUMN` is fast but does not reclaim space; see
  https://www.postgresql.org/docs/current/sql-altertable.html (verified 2026-11-01).
- [invariant] Set `idle_in_transaction_session_timeout` for application roles and keep transactions short.
  Why: an open transaction holds locks, delays DDL, and prevents vacuum from removing rows that only it can still
  see. Test: `BEGIN; SELECT 1;` and wait longer than the timeout; the session is terminated. Source:
  https://www.postgresql.org/docs/current/runtime-config-client.html,
  https://www.postgresql.org/docs/current/routine-vacuuming.html (verified 2026-11-01).

### Transactions and errors

- [invariant] After any error inside a transaction block, the transaction is aborted. To continue, roll back to a
  savepoint, or use `INSERT ... ON CONFLICT` so no error is raised. Do not catch a unique violation and carry on
  in the same transaction. Why: PostgreSQL rejects every later statement until rollback; SQLite and MySQL
  behave differently, so the bug appears only on PostgreSQL. Test: `BEGIN; INSERT` a duplicate (error), then
  `SELECT 1` fails with "current transaction is aborted, commands ignored until end of transaction block", and
  `COMMIT` rolls back (PostgreSQL 17.10, 2026-11-01); with `SAVEPOINT s` before the insert and `ROLLBACK TO
  SAVEPOINT s` after it, the later insert commits. Source:
  https://www.postgresql.org/docs/current/tutorial-transactions.html,
  https://www.postgresql.org/docs/current/sql-insert.html (verified 2026-11-01).
- [invariant] Retry the whole transaction on SQLSTATE `40001` (serialization failure) and `40P01` (deadlock),
  with a bounded count and jitter. Why: these errors are expected under concurrency and the second attempt
  usually succeeds; the application must be prepared for them. Test: two Repeatable Read transactions update the
  same row; the second fails with "could not serialize access due to concurrent update" and succeeds when
  re-run from `BEGIN`. Source: https://www.postgresql.org/docs/current/transaction-iso.html,
  https://www.postgresql.org/docs/current/errcodes-appendix.html (verified 2026-11-01).
- [default] Stay on Read Committed (the default). Use `FOR UPDATE`, a unique constraint or an advisory lock for a
  single invariant; use Serializable only with the retry loop above. Trade-off: Read Committed allows
  non-repeatable reads inside one transaction. Deviate only with an ADR that names this trade-off. Source:
  https://www.postgresql.org/docs/current/transaction-iso.html (verified 2026-11-01).

### Connection pooling

- [invariant] Behind PgBouncer in transaction mode, use no session state. Replace `SET` with `SET LOCAL` inside
  the transaction, session advisory locks with `pg_advisory_xact_lock`, and do not use `LISTEN`, `PREPARE` or
  `DEALLOCATE` statements. Protocol-level prepared statements need `max_prepared_statements` set to a non-zero
  value. Why: the server connection changes between transactions, so session state lands on another client's
  connection or is gone. Test: with `pool_mode = transaction`, `SET statement_timeout = '1s'` followed by a query
  in the next transaction may run on a connection without it; `SET LOCAL` inside the transaction holds. Source:
  https://www.pgbouncer.org/features.html, https://www.pgbouncer.org/config.html,
  https://www.postgresql.org/docs/current/sql-set.html (verified 2026-11-01).

### Types and keys

- [default] Store points in time as `timestamptz`, never `timestamp`. Trade-off: none that matters outside
  calendar-picture data such as "opens at 09:00 local". Deviate only with an ADR that names this trade-off.
  Source: https://www.postgresql.org/docs/current/datatype-datetime.html,
  https://wiki.postgresql.org/wiki/Don%27t_Do_This (verified 2026-11-01). Test: store `2026-11-01 12:00` in both
  types under `UTC`, switch to `Asia/Tokyo`; `timestamptz` reads back `21:00+09`, `timestamp` unchanged, and they
  compare unequal.
- [default] Use `bigint GENERATED ... AS IDENTITY` for internal keys, not `serial`. For a uuid key on PostgreSQL
  18 or later prefer `uuidv7()`; random v4 values insert at random index positions. Public identifier rules are
  in `dual-key-identifiers`. Trade-off: uuid keys are 16 bytes and need a generator before version 18. Deviate
  only with an ADR that names this trade-off. Source: https://wiki.postgresql.org/wiki/Don%27t_Do_This,
  https://www.postgresql.org/docs/current/functions-uuid.html (`uuidv7()` is time-ordered; it is new in 18 per
  https://www.postgresql.org/docs/release/18.0/). The index-locality consequence is design judgment (verified
  2026-11-01).
- [default] Use `jsonb` for sparse or externally shaped data. Columns you filter, join, order by or constrain are
  real columns. Keep documents small. Trade-off: more columns and migrations. Deviate only with an ADR that names
  this trade-off. Source: https://www.postgresql.org/docs/current/datatype-json.html (any update locks the whole
  row; documents should be atomic data) (verified 2026-11-01).

### Operations

- [default] Leave autovacuum on and tune it per table (storage parameters) for hot tables. Never schedule
  `VACUUM FULL` as routine care. Trade-off: per-table settings are one more thing to track. Deviate only with an
  ADR that names this trade-off. Source: https://www.postgresql.org/docs/current/routine-vacuuming.html,
  https://www.postgresql.org/docs/current/sql-vacuum.html (`VACUUM FULL` locks the table exclusively and needs
  disk for a full copy) (verified 2026-11-01).
- [default] Diagnose slow queries with `EXPLAIN (ANALYZE, BUFFERS)` on production-sized data, and wrap
  `ANALYZE` of a write in `BEGIN ... ROLLBACK`. Trade-off: the statement really runs. Deviate only with an ADR
  that names this trade-off. Source: https://www.postgresql.org/docs/current/sql-explain.html (`ANALYZE`
  executes the statement; `BUFFERS` is on by default with `ANALYZE` from 18, per
  https://www.postgresql.org/docs/release/18.0/) (verified 2026-11-01). Test: `EXPLAIN ANALYZE DELETE ...`
  inside `BEGIN`/`ROLLBACK` leaves the rows in place.
- [default] Enable `pg_stat_statements` and rank by total time before tuning. Trade-off: it needs
  `shared_preload_libraries` and a restart. Deviate only with an ADR that names this trade-off. Source:
  https://www.postgresql.org/docs/current/pgstatstatements.html (verified 2026-11-01).
- [invariant] Run the required test suite on PostgreSQL, not on an in-memory engine; `verify-before-done` states
  the rule and its test. Why: an aborted transaction, a missing `ORDER BY` and a lock conflict never show on
  SQLite. Test: the duplicate-insert case above passes on SQLite and fails on PostgreSQL. Source:
  https://www.postgresql.org/docs/current/tutorial-transactions.html (verified 2026-11-01).

## Procedure

1. Name the PostgreSQL major version the target runs. Rules marked with a major (11, 12, 15, 16, 18) depend on it.
2. For a migration, split it into expand, backfill and contract steps. Read
   [references/migrations.md](references/migrations.md) for the statement recipes and the lock levels.
3. Run the linter on every new migration file and fix each finding or justify it inline:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/pg_lint_migration.py path/to/migrations`. Exit code 1 means an error.
4. For queries and indexes, read [references/indexes-and-queries.md](references/indexes-and-queries.md): keyset
   SQL, the detection queries for unused, duplicate and missing-foreign-key indexes, and the `EXPLAIN` workflow.
5. For application transaction code or a pooler, read
   [references/pooling-and-transactions.md](references/pooling-and-transactions.md): savepoints, the retry loop
   and the pooler compatibility table.
6. Test on PostgreSQL at the production major. `verify-before-done` defines what may be called done. For backups
   and point-in-time recovery see `high-availability`.
7. A project may also install a third-party PostgreSQL skill. This skill takes precedence on the invariants
   listed above; take the rest of the third-party advice as input and check it against the manual.

## Traps

- A migration that is fast on a 10,000-row dev database and holds ACCESS EXCLUSIVE for minutes on production,
  because the lock waits behind one open transaction and the scan runs under the lock.
- A migration framework that wraps every file in a transaction: `CREATE INDEX CONCURRENTLY` fails there. Disable
  the wrapper for that file only.
- A failed `CREATE INDEX CONCURRENTLY` that leaves an invalid index; the retry fails with "already exists".
- An `except IntegrityError: pass` in a get-or-create helper, green on SQLite and broken on PostgreSQL.
- A cleanup job that runs `UPDATE ... SET x = ...` over the whole table in one transaction and blocks vacuum and
  replicas while it runs.
- `statement_timeout` set with `SET` through a transaction pooler, applied to a different client's connection.
- An unused index judged on a replica's counters, or on counters reset by a restore.
- `ORDER BY created_at LIMIT 20` with many identical timestamps, so page two repeats rows from page one.

## Done when

- Every migration passes `pg_lint_migration.py` with no unexplained finding, and each inline allow names a reason.
- Locking statements run under `lock_timeout` and are retried; no DDL shares a transaction with a large data
  change.
- New indexes were built concurrently, and no invalid index remains in `pg_index`.
- Queries bind their values, sort uniquely, and paginate by key where the list can grow.
- Transaction code uses savepoints or `ON CONFLICT`, and retries 40001 and 40P01.
- The tests ran on PostgreSQL at the production major version.

## References

- [references/migrations.md](references/migrations.md): read when you write or review a schema change, a
  backfill or a type change, or when a migration hangs on a lock.
- [references/indexes-and-queries.md](references/indexes-and-queries.md): read when you design an index, paginate
  a list, hunt unused indexes or read a slow query plan.
- [references/pooling-and-transactions.md](references/pooling-and-transactions.md): read when you handle a
  database error in application code, choose an isolation level, or put a pooler in front of PostgreSQL.

## Sources

- https://www.postgresql.org/support/versioning/: current major 18 (18.6), support window, verified 2026-11-01.
- https://www.postgresql.org/docs/current/sql-altertable.html: lock levels, `NOT VALID`, `VALIDATE CONSTRAINT`,
  rewrite behaviour, `SET NOT NULL` shortcut, verified 2026-11-01.
- https://www.postgresql.org/docs/current/sql-createindex.html: `CONCURRENTLY` caveats, verified 2026-11-01.
- https://www.postgresql.org/docs/current/explicit-locking.html: lock modes and conflicts, locks held to the end of
  the transaction, deadlocks, advisory locks, verified 2026-11-01.
- https://www.postgresql.org/docs/current/transaction-iso.html: isolation levels and retry duty, verified 2026-11-01.
- https://www.postgresql.org/docs/current/tutorial-transactions.html: aborted state and `ROLLBACK TO`, verified
  2026-11-01.
- https://www.pgbouncer.org/features.html: SQL feature map for pooling modes, verified 2026-11-01.
- https://www.pgbouncer.org/config.html: `pool_mode` and `max_prepared_statements`, verified 2026-11-01.
- Local runs on PostgreSQL 17.10 (official `postgres:17-alpine` image) on 2026-11-01: the abort after a unique
  violation, the savepoint recovery, `CREATE INDEX CONCURRENTLY` inside a transaction, the filenode check for
  `ADD COLUMN`, the lock queue behind `ALTER TABLE`, the `SET NOT NULL` shortcut, `NOT IN` with NULL, the
  `timestamptz` comparison. The PgBouncer rule rests on the vendor pages only; no pooler was run.
