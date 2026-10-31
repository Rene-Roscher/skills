# Production read access

Load this after the user approved a read of production data. The approval covers the question that was asked, not
the database in general.

## Before connecting

- Use the read path the project's runbook names: a read replica, a hot standby, or a role with read grants only.
- Get the credential from the place the runbook names. If it must sit in a local file for the check, set mode 0600
  and delete the file when you are done. Restore any edited env file byte for byte.
- Don't print the connection string, the password or a token in the conversation or in a log.

## Server-side checks (PostgreSQL)

- Run `SELECT pg_is_in_recovery();` at the start of every session. It returns true while the server is a standby.
  If it returns false, stop: the server was promoted, and the session can now write.
- Hot standby sessions are read-only while standby lasts. Once it ends, a session that began during standby can
  start read-write transactions. Keep sessions short and reconnect for each question.
- `default_transaction_read_only` sets a default that the session can change. Use it as a seatbelt on top of a
  read-only role, never instead of one.
- Set a statement timeout for the session so a heavy query can't hurt the primary through replication or locks.

For other engines, look up the server-side equivalent (read-only role, replica state) in that engine's
documentation before you rely on it.

## Scoping queries

- Answer the question with counts and aggregates where you can, not with rows.
- Select only the columns you need. Never `SELECT *` on tables that hold personal data.
- Add a `LIMIT` to every exploratory query.
- Check the plan with `EXPLAIN` (not `EXPLAIN ANALYZE`, which runs the query) before a query that may scan a large
  table.

## Reporting

- Report counts, shapes and public identifiers. Leave out internal sequential IDs, names, email addresses, phone
  numbers and free-text fields.
- If a row must be referenced, use its public ID or describe its shape ("an order with three line items and a
  refunded payment").
- Don't paste query results with personal data into tickets, commits, fixtures or chat.

## Sources

- https://www.postgresql.org/docs/17/hot-standby.html (hot standby is read-only; read-write after standby ends),
  verified 2026-10.
- https://www.postgresql.org/docs/17/functions-admin.html (`pg_is_in_recovery()`), verified 2026-10.
- https://www.postgresql.org/docs/17/runtime-config-client.html (`default_transaction_read_only`,
  `statement_timeout`), verified 2026-10.
- https://www.postgresql.org/docs/17/sql-explain.html (`EXPLAIN ANALYZE` executes the statement), verified 2026-10.
