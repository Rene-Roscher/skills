# Pooling and transactions

## Contents

- Aborted transactions and savepoints
- Retry loop
- Isolation level choice
- Advisory locks and row locks
- PgBouncer pooling modes
- Long transactions

Statements ran on PostgreSQL 17.10 on 2026-11-01 where the text says so. PgBouncer behaviour comes from the vendor
pages only; no pooler was run for this skill.

## Aborted transactions and savepoints

Ran:

```sql
BEGIN;
INSERT INTO t(email) VALUES ('a@example.com');
INSERT INTO t(email) VALUES ('a@example.com');   -- ERROR: duplicate key value violates unique constraint
SELECT 1;   -- ERROR: current transaction is aborted, commands ignored until end of transaction block
COMMIT;     -- reports ROLLBACK; the first insert is gone
```

The manual: `ROLLBACK TO` is the only way to regain control of a transaction block that the system put in aborted
state, short of rolling it back completely (https://www.postgresql.org/docs/current/tutorial-transactions.html,
verified 2026-11-01). With a savepoint around the risky statement, the transaction continues:

```sql
BEGIN;
INSERT INTO t(email) VALUES ('b@example.com');
SAVEPOINT s;
INSERT INTO t(email) VALUES ('b@example.com');   -- error
ROLLBACK TO SAVEPOINT s;
INSERT INTO t(email) VALUES ('c@example.com');
COMMIT;      -- b and c are stored
```

Choices, in order of preference:

1. Avoid the error: `INSERT ... ON CONFLICT DO NOTHING` (or `DO UPDATE`) raises no error for the conflict
   (https://www.postgresql.org/docs/current/sql-insert.html, verified 2026-11-01).
2. Savepoint per risky statement when you need to know that it failed and still continue.
3. One transaction per unit of work, and let the error roll everything back.

Framework "nested transaction" helpers usually map to savepoints; a try/catch around a plain query without one does
not. `SET` and `SET LOCAL` changes made after a savepoint are cancelled by rolling back to it
(https://www.postgresql.org/docs/current/sql-set.html, verified 2026-11-01). A lock taken after a savepoint is
released when you roll back to it (https://www.postgresql.org/docs/current/explicit-locking.html, verified
2026-11-01). Savepoints are not free: use them around the statement that can fail, not around every statement.
Unverified: the exact cost of many savepoints per transaction on a specific version; measure before relying on it.

## Retry loop

Retry the whole transaction, from `BEGIN`, on:

| SQLSTATE | Name | Source |
|---|---|---|
| `40001` | serialization_failure | https://www.postgresql.org/docs/current/errcodes-appendix.html |
| `40P01` | deadlock_detected | https://www.postgresql.org/docs/current/errcodes-appendix.html |

(verified 2026-11-01). Rules for the loop:

- Retry the complete transaction, including its reads: the second attempt sees a new snapshot, and the manual
  states that applications at Repeatable Read and Serializable must be prepared to retry
  (https://www.postgresql.org/docs/current/transaction-iso.html, verified 2026-11-01).
- Bound the attempts (3 to 5 is a common choice; the number is design judgment) and add random delay so conflicting
  transactions do not retry in lockstep.
- Do side effects (mail, HTTP calls, queue publishes) after commit or through an outbox written in the same
  transaction, because a retried attempt would repeat them.
- Do not retry unique violations (`23505`) blindly. They are a result, not a transient failure.
- To lower deadlocks, take row locks in a consistent order, for example `ORDER BY id` in `SELECT ... FOR UPDATE`
  (https://www.postgresql.org/docs/current/explicit-locking.html, verified 2026-11-01).

Ran: two Repeatable Read transactions updated the same row; the second received "could not serialize access due to
concurrent update". The manual documents that message for this case.

## Isolation level choice

- Read Committed is the default. A `SELECT` sees data committed before the query began, each statement sees a new
  snapshot, and Read Uncommitted behaves like Read Committed in PostgreSQL.
- Repeatable Read gives one snapshot per transaction and fails with a serialization error on concurrent update of a
  row you read or wrote.
- Serializable emulates serial execution and needs the retry loop; data read must not be treated as valid until
  commit, even in read-only transactions (except deferrable ones).
- Pick the weakest level that keeps one named invariant, and write the invariant down. For a single-row invariant,
  prefer `SELECT ... FOR UPDATE` or a unique constraint at Read Committed.

Source: https://www.postgresql.org/docs/current/transaction-iso.html (verified 2026-11-01).

## Advisory locks and row locks

- Session-level advisory locks do not honour transaction semantics: a lock taken in a transaction that rolls back is
  still held, until it is released or the session ends. Transaction-level ones (`pg_advisory_xact_lock`) release at
  transaction end.
- Advisory locks live in shared memory with a limit; with `ORDER BY` plus `LIMIT` the lock function can run for rows
  that are later discarded (manual example in the same section).

Source: https://www.postgresql.org/docs/current/explicit-locking.html (verified 2026-11-01).

## PgBouncer pooling modes

`pool_mode` is `session` (default), `transaction` or `statement`
(https://www.pgbouncer.org/config.html, verified 2026-11-01). The vendor's SQL feature map for transaction
pooling (https://www.pgbouncer.org/features.html, verified 2026-11-01) says transaction pooling "breaks client
expectations of the server by design":

| Feature | Session pooling | Transaction pooling |
|---|---|---|
| `SET` / `RESET` | Yes | Never |
| `LISTEN` | Yes | Never |
| `NOTIFY` | Yes | Yes |
| `WITH HOLD` cursor | Yes | Never |
| Protocol-level prepared plans | Yes | Yes, with `max_prepared_statements` non-zero |
| `PREPARE` / `DEALLOCATE` | Yes | Never |
| `ON COMMIT DROP` temp tables | Yes | Yes |
| `PRESERVE`/`DELETE ROWS` temp tables | Yes | Never |
| Session-level advisory locks | Yes | Never |

Startup parameters (`client_encoding`, `DateStyle`, `IntervalStyle`, `Timezone`, `standard_conforming_strings`,
`application_name`) are tracked and stay consistent. Everything else set with `SET` does not.

Consequences for application code:

- Put per-request settings in `SET LOCAL` inside the transaction, or in the role's or database's defaults
  (`ALTER ROLE ... SET`), not in a session `SET` after connect.
- Replace `pg_advisory_lock` with `pg_advisory_xact_lock`, or run the work on a direct (session-mode) connection.
- A client library that sends `PREPARE` as a SQL statement fails; one that uses the protocol's prepared statements
  works only when `max_prepared_statements` is set. Check the driver's option for disabling server-side prepared
  statements. Unverified: which driver exposes which option; read your driver's documentation.
- `LISTEN` and long-lived session features (migrations that rely on session settings, `pg_dump`, schema tools) use a
  direct connection or a session-mode pool.
- Run migrations over a direct connection: `lock_timeout` set with a plain `SET` is lost when the pooler hands the
  next transaction to another server connection.

## Long transactions

An open transaction holds its locks until the end and, even when it holds no significant locks, prevents vacuum
from removing recently dead rows that only it can see, which feeds bloat
(https://www.postgresql.org/docs/current/runtime-config-client.html, `idle_in_transaction_session_timeout`;
https://www.postgresql.org/docs/current/routine-vacuuming.html, verified 2026-11-01). Find them:

```sql
SELECT pid, state, now() - xact_start AS xact_age, left(query, 80) AS query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start
LIMIT 10;
```

The vacuum chapter advises ending long-running open transactions found through `pg_stat_activity`. Set
`idle_in_transaction_session_timeout` for application roles. Autovacuum is on by default and tunable per table; the
default scale factor is 0.2, so a very large table waits for a large number of dead rows before vacuuming
(https://www.postgresql.org/docs/current/runtime-config-vacuum.html, verified 2026-11-01). `VACUUM FULL` locks the
table exclusively and writes a full copy, so it is a last resort (https://www.postgresql.org/docs/current/sql-vacuum.html,
verified 2026-11-01).
