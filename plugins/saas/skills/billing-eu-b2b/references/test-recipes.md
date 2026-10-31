# Test recipes

Load when writing concurrency tests, recorded fixtures or transaction-level assertions for billing code.

## Run on the production engine and runtime

- Billing tests that count run on PostgreSQL (or whatever production uses). An in-memory SQLite lane is fine
  for speed, but it accepts writes that PostgreSQL rejects (CHECK constraints), does not abort a transaction on
  a caught unique violation, and returns rows in a different default order.
- The test bootstrap aborts when the PHP (or Node, Go) minor version differs from production's.

## Concurrency

A sequential test cannot show a race. Use real parallelism against a real database:

- Two or more database connections, each in its own transaction, interleaved by the test: connection A reads,
  connection B reads, A inserts and commits, B inserts. Assert the outcome (one effect, one success).
- Or fire N parallel HTTP requests at a running test server and count the results.
- Or fork worker processes that each run the code path once, then assert in the parent.

Each recipe needs its own database state per run, committed (not inside a wrapping test transaction, which
would hide the race), and cleaned up afterwards.

Cases: two webhook deliveries of one event; two renewal runs for one period; N creates at limit minus one; two
debits of a balance that covers only one.

## Transaction level at the PSP call

The fake PSP client records whether a database transaction was open when it was called. In Laravel that is
`DB::transactionLevel()`; with a test that wraps each case in a transaction, compare against the baseline
level instead of 0.

## Recorded fixtures

- Record one real response per endpoint and outcome from the provider's sandbox (or a documented example in
  the provider's docs), strip secrets and personal data, and store it under the tests' fixtures directory.
- Each file names its source (endpoint or docs URL) and recording date. A test fails on a fixture without them.
- The fake returns fixtures; it never builds response shapes by hand.

## Property and table tests

- The money helper: every net from 0 to a high cent value, for every configured rate, against an exact
  decimal reference.
- Proration: parts never exceed the whole for random prices, periods and switch dates.
- Tax resolver: one row per (seller country, buyer country, business confirmed, VAT ID status).

## Mutation testing

Optional, restricted to money code. Pest has a `--mutate` option with `--min` for a required score, and the
tests name what they cover with `covers()` or `mutates()` (https://pestphp.com/docs/mutation-testing,
verified 2026-10-31).
