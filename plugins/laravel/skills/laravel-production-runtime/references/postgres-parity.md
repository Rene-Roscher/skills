# PostgreSQL parity

Load when writing migrations, upserts, JSON columns, timestamps or aggregates, or when setting up the
PostgreSQL CI lane. Each item was reproduced on PostgreSQL 16.11 and SQLite 3.45.1 on 2026-10-31, or quoted
from the PostgreSQL docs.

## Contents

- The lane
- Aborted transactions and unique violations
- jsonb
- timestamp precision
- CHECK constraints
- Aggregates and raw expressions
- Ordering
- Drift canary file

## The lane

- A second PHPUnit config (for example `phpunit.pg.xml`) points the suite at PostgreSQL, with its own database
  name. Parallel runs from several sessions each get their own database, or they corrupt each other.
- The PostgreSQL job is a required check. The SQLite lane may stay as the fast loop.
- Migrations run from scratch in the lane. A migration that is pending in a dev database is invisible to a
  suite that builds its schema from the migration files, so check `migrate:status` against the target
  environment separately.

## Aborted transactions and unique violations

After any error inside a transaction block, PostgreSQL ignores every further command until `ROLLBACK`, or
`ROLLBACK TO` a savepoint (https://www.postgresql.org/docs/current/tutorial-transactions.html,
https://www.postgresql.org/docs/current/sql-savepoint.html). SQLite carries on. So this passes on SQLite and
fails on PostgreSQL:

```php
DB::transaction(function () use ($event): void {
    try {
        WebhookReceipt::create(['provider_event_id' => $event->id]);
    } catch (QueryException) {
        // duplicate, ignore
    }
    $this->process($event); // PostgreSQL: current transaction is aborted
});
```

Fixes, in order of preference:

- Insert on conflict: `insertOrIgnore()` or `upsert()`, which do not raise on the duplicate.
- `createOrFirst()` or `firstOrCreate()`: in framework v12.53.0, `createOrFirst()` wraps the insert in
  `withSavepointIfNeeded()` and catches `UniqueConstraintViolationException`, and `firstOrCreate()` falls back to
  it (`src/Illuminate/Database/Eloquent/Builder.php`).
- A nested `DB::transaction()` around the attempt, which becomes a savepoint inside the outer transaction.

Prefer insert-on-conflict over check-then-insert: `exists()` followed by `create()` races under concurrent
deliveries.

## jsonb

jsonb stores a parsed form: it does not keep key order, and of duplicate keys only the last survives
(https://www.postgresql.org/docs/current/datatype-json.html). `SELECT '{"b":1,"a":2,"b":3}'::jsonb` returns
`{"a": 2, "b": 3}`. Compare decoded arrays in tests, never JSON strings.

## timestamp precision

`timestamptz(0)` rounds fractional seconds, it does not truncate: `'2024-01-01 00:00:00.6+00'::timestamptz(0)`
gives `00:00:01`, and `.5` also rounds up. Values with fractions come from database defaults such as `now()`,
raw inserts, or dates formatted with microseconds. A row can land in the next second, which flips same-second
ordering and equality assertions. Freeze time in tests and compare at the precision the column stores.

## CHECK constraints

Constraints added for PostgreSQL only (driver-branched migrations) do not exist in the SQLite schema, so fixtures
that violate them pass there. Mirror each constraint's allowed values in a PHP constant or enum that validation
also uses, and prove the constraint with a PostgreSQL-only test that inserts an invalid value and expects the
violation.

## Aggregates and raw expressions

PostgreSQL names `count(*)` as `count`; SQLite names it `count(*)`. Code that reads the column by name, such as
`pluck(DB::raw('count(*)'))`, works on one engine only. Alias every raw expression:
`selectRaw('count(*) as total')`.

## Ordering

Without `ORDER BY`, row order is undefined, and engines differ. Every query whose order matters (invoice lines,
exports, paginated lists) orders explicitly, with a unique tie-breaker.

## Drift canary file

`tests/Feature/Database/PostgresDriftCanaryTest.php`, skipped outside the PostgreSQL lane, with one test per
item above: jsonb comparison, unique violation inside a transaction handled without aborting it,
`timestamptz(0)` rounding, each CHECK constraint, aliased aggregates, explicit order.
