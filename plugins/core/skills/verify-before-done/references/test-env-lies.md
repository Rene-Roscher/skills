# How the test environment lies

Load when tests are green but you doubt production behaviour, or when you write a guard.

Each section names a difference between the test run and production, and the check that exposes it.

## Database engine

An in-memory or embedded engine accepts what the production engine rejects, and the reverse. Known gaps when
the production engine is PostgreSQL:

- An error inside a transaction puts the whole block in aborted state. Every later statement fails until a
  rollback, so a caught unique violation breaks the rest of the transaction. Embedded engines often continue.
- Without `ORDER BY`, row order is unspecified. A test that relies on insert order can pass on one engine and
  fail on another.
- `jsonb` does not keep key order or duplicate keys, so a test that compares JSON text can fail.
- `CHECK` constraints and strict types reject fixtures that a looser engine stores.

Check: the required CI job runs the suite on the production engine.

Sources: https://www.postgresql.org/docs/current/tutorial-transactions.html,
https://www.postgresql.org/docs/current/queries-order.html, https://www.postgresql.org/docs/current/datatype-json.html
(verified 2026-10).

## Runtime minor

A minor version can change results: PHP 8.4 changed `round()` for some float edge cases. Keep the target
version in one place and have the test bootstrap abort when the running minor differs.

Source: https://github.com/php/php-src/blob/PHP-8.4/UPGRADING (verified 2026-10).

## Sync versus async

Queues often run synchronously in tests and asynchronously in production. A guard that reads data a queued
job writes never sees it in production at the time it runs.

Check: run the guard's test with the queue faked, so the job's write is absent, and assert the guard still
holds.

## Fakes that do not render

A mail or notification fake records that a message was sent without rendering it. Escaping errors, broken
links and missing variables go unseen.

Check: render each changed template once for real and assert on the output.

## Test-only configuration and components

Values forced by the test config may never reach the app the way production sets them. A component booted
only in the test environment, or only in the web process, is missing in queue workers.

Check: an environment pin test asserts, from inside the running app, each value the test config forces. For
jobs, run one job in a worker process the way production does.

## Schema state

A suite that builds its schema from migration files sees a migration that was never applied to any real
database.

Check: the framework's migration status on the dev database shows nothing pending before an end-to-end claim.

## Time

Several writes in the same second share a timestamp, and counters depend on the clock. A query-count test can
vary when a second boundary passes during the run.

Check: freeze the clock in tests that count queries or compare timestamps.

## Shared stores

Tests that read or write a shared dev database, cache or metrics store see dev data and can delete it.

Check: tests use their own database or prefix. Point the shared store's address at an unreachable host in CI
to see which tests depend on it.

## Dev doubles

A mock endpoint in the dev stack serves canned data instead of the real service, so the frontend looks right
while the real emitter is broken.

Check: name which parts of the dev stack are mocks, and verify the real emitter separately.
