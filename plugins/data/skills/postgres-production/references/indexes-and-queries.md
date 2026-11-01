# Indexes and queries

## Contents

- Keyset pagination
- Index design checks
- Detection queries
- EXPLAIN workflow
- pg_stat_statements
- MERGE and upsert

Statements ran on PostgreSQL 17.10 on 2026-11-01 where the text says so; other claims cite the manual page for the
current major (18), verified 2026-11-01.

## Keyset pagination

```sql
-- first page
SELECT id, created_at, title FROM ticket
WHERE tenant_id = $1
ORDER BY created_at DESC, id DESC
LIMIT 21;                      -- one extra row tells you there is a next page

-- next page: pass the last row's created_at and id
SELECT id, created_at, title FROM ticket
WHERE tenant_id = $1 AND (created_at, id) < ($2, $3)
ORDER BY created_at DESC, id DESC
LIMIT 21;
```

- Index to match: `(tenant_id, created_at DESC, id DESC)`, equality column first
  (https://www.postgresql.org/docs/current/indexes-multicolumn.html, verified 2026-11-01).
- The row comparison runs left to right and stops at the first unequal pair. A NULL in a compared column makes the
  result unknown, so keep sort columns NOT NULL (https://www.postgresql.org/docs/current/functions-comparisons.html,
  verified 2026-11-01).
- The cursor sent to clients is opaque (encode the two values); do not put internal keys in URLs unreviewed
  (`dual-key-identifiers`).
- Reverse direction and "previous page" need the mirrored comparison and sort; test both on a table with duplicate
  `created_at` values.
- `OFFSET` is acceptable for a small bounded list: skipped rows are still computed, so cost grows with the offset
  (https://www.postgresql.org/docs/current/queries-limit.html, verified 2026-11-01).

## Index design checks

1. Equality columns first, then one range or sort column; the leading columns decide how much of the index is
   scanned (https://www.postgresql.org/docs/current/indexes-multicolumn.html, verified 2026-11-01).
2. Prefer a partial index for a stable subset such as active rows; the query's `WHERE` must imply the index
   predicate (https://www.postgresql.org/docs/current/indexes-partial.html, verified 2026-11-01).
3. `INCLUDE (col)` adds non-key columns for index-only scans; the table's visibility map must be current, so an
   index-only scan still depends on vacuum (https://www.postgresql.org/docs/current/indexes-index-only-scans.html,
   https://www.postgresql.org/docs/current/sql-createindex.html, verified 2026-11-01).
4. A foreign key does not create an index on the referencing column, and a delete or key update on the parent scans
   the child without one (https://www.postgresql.org/docs/current/ddl-constraints.html, verified 2026-11-01).
5. Every index costs writes and disk. A unique index is also a constraint; keep it even when unread.
6. `jsonb` containment queries use a GIN index; the manual describes the `jsonb_ops` and `jsonb_path_ops` classes
   (https://www.postgresql.org/docs/current/datatype-json.html, verified 2026-11-01). Index a frequently filtered
   key as an ordinary column instead when you can.

## Detection queries

Unused indexes (judge on every server that serves reads, after a full business cycle; counters reset after an
unclean shutdown, a base backup or point-in-time recovery):

```sql
SELECT s.relname, s.indexrelname, s.idx_scan, pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes s
JOIN pg_index i USING (indexrelid)
WHERE s.idx_scan = 0 AND NOT i.indisunique
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

Exact duplicates (same table, columns, operator classes, sort options, predicate and expressions):

```sql
SELECT indrelid::regclass AS tbl, array_agg(indexrelid::regclass) AS duplicates
FROM pg_index
GROUP BY indrelid, indkey, indclass, indoption, indpred, indexprs
HAVING count(*) > 1;
```

Foreign keys whose referencing columns are not the leading columns of any valid index (exact column order match;
this misses an index that has the key columns first and more after, so read hits as candidates):

```sql
SELECT conrelid::regclass AS tbl, conname
FROM pg_constraint c
WHERE contype = 'f' AND NOT EXISTS (
  SELECT 1 FROM pg_index i
  WHERE i.indrelid = c.conrelid AND i.indisvalid
    AND (i.indkey::int2[])[0:cardinality(c.conkey) - 1] = c.conkey::int2[]);
```

Invalid indexes left by a failed concurrent build: `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`

Ran against a scratch database: the duplicate query listed two identical indexes, the unused query listed both with
`idx_scan = 0`, the foreign key query listed the unindexed key. Sources: https://www.postgresql.org/docs/current/monitoring-stats.html,
https://www.postgresql.org/docs/current/catalog-pg-index.html (verified 2026-11-01). `last_idx_scan` is available
from PostgreSQL 16 for "when was it last used".

## EXPLAIN workflow

1. Capture the slow statement with real parameter values from `pg_stat_statements` or the application log.
2. `EXPLAIN (ANALYZE, BUFFERS) <statement>` on data of production size. `ANALYZE` executes the statement; for
   `INSERT`, `UPDATE`, `DELETE`, `MERGE` wrap it in `BEGIN; ... ROLLBACK;`. `BUFFERS` is included automatically with
   `ANALYZE` from PostgreSQL 18, so add it explicitly on older majors (https://www.postgresql.org/docs/current/sql-explain.html,
   https://www.postgresql.org/docs/release/18.0/, verified 2026-11-01).
3. Compare estimated and actual row counts per node; a large gap points at stale statistics (`ANALYZE`) or a
   predicate the planner cannot estimate.
4. Read buffers: many `shared read` blocks mean cold data or a scan that touches too much; `temp` blocks mean a sort
   or hash spilled to disk.
5. Change one thing (an index, a rewrite), rerun, compare. A sequential scan on a tiny table is correct.
6. `EXPLAIN (GENERIC_PLAN)` shows the plan for a statement with `$1` placeholders and cannot be combined with
   `ANALYZE` (same manual page).

## pg_stat_statements

Needs `shared_preload_libraries = 'pg_stat_statements'` and a restart, then `CREATE EXTENSION pg_stat_statements`.
Rank by `total_exec_time` first (calls times mean), then by `mean_exec_time` for single slow statements. The view
has `calls`, `total_exec_time` and `mean_exec_time` columns. Source:
https://www.postgresql.org/docs/current/pgstatstatements.html (verified 2026-11-01).

## MERGE and upsert

- `INSERT ... ON CONFLICT DO UPDATE` guarantees an atomic insert or update even under high concurrency, and `DO
  NOTHING` skips conflicting rows without raising an error (https://www.postgresql.org/docs/current/sql-insert.html,
  verified 2026-11-01). It needs a unique index or constraint as arbiter.
- `MERGE` exists from PostgreSQL 15 (release notes 15; the 14 manual has no MERGE page). Use it for multi-branch
  sync logic. Run concurrently with other writers it follows the usual isolation rules, and the `MERGE` page
  itself points to `INSERT ... ON CONFLICT` as an alternative with a stronger guarantee for insert-or-update
  (https://www.postgresql.org/docs/current/sql-merge.html, verified 2026-11-01). Prefer `ON CONFLICT` for a plain
  "insert or update by key".
- `UNIQUE NULLS NOT DISTINCT` (PostgreSQL 15) makes NULLs equal for uniqueness. By default NULLs are distinct, so a
  nullable unique column accepts many NULL rows (https://www.postgresql.org/docs/current/sql-createtable.html,
  https://www.postgresql.org/docs/release/15.0/, verified 2026-11-01).
