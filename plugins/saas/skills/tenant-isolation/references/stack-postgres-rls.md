# PostgreSQL row-level security

Load when adopting or reviewing RLS. RLS is a second line behind explicit scoping, not a replacement. Facts below are
from the PostgreSQL 18 docs and the PgBouncer docs, verified 2026-10-31. Re-read them for the deployed versions.

## Who bypasses RLS

- "If no policy exists for the table, a default-deny policy is used, meaning that no rows are visible or can be
  modified."
- "Superusers and roles with the `BYPASSRLS` attribute always bypass the row security system when accessing a
  table."
- "Table owners normally bypass row security as well, though a table owner can choose to be subject to row security
  with ALTER TABLE ... FORCE ROW LEVEL SECURITY."
- "Referential integrity checks, such as unique or primary key constraints and foreign key references, always
  bypass row security", which the docs call a possible "covert channel".

Source: https://www.postgresql.org/docs/current/ddl-rowsecurity.html.

Consequences:

- The application connects as a dedicated role that owns no tables and has no `BYPASSRLS`. Migrations run as the
  owner role.
- Set `FORCE ROW LEVEL SECURITY` on every tenant table anyway, so a misconfigured owner connection still filters.
- A unique constraint on a column that tenants choose freely (a project key, a slug) tells tenant A that tenant B
  already uses the value. Make such constraints per tenant, `(tenant_id, key)`.

## Passing the tenant to the policy

Policies read the tenant from a setting, for example `current_setting('app.tenant_id', true)`. With `missing_ok` set
to true, an unset setting returns NULL instead of an error
(https://www.postgresql.org/docs/current/functions-admin.html), so a policy comparing `tenant_id` to it matches no
rows. That is the fail-closed behaviour you want. Test the policy twice: with the setting never set in the session,
and after a transaction that set it has ended. Both must return no rows or an error, never rows.

Set the value per transaction, not per session:

- `set_config('app.tenant_id', $1, true)`: with `is_local` true "the new value will only apply during the current
  transaction" (https://www.postgresql.org/docs/current/functions-admin.html).
- Run it as the first statement of every transaction that touches tenant tables, in the same transaction as the
  queries.

## Behind a connection pooler

- PgBouncer lists `SET`/`RESET` as never supported in transaction pooling
  (https://www.pgbouncer.org/features.html).
- In transaction pooling, `server_reset_query` is not used, and "each transaction ends up in a different connection
  and thus gets a different session state" (https://www.pgbouncer.org/config.html).
- So a session-level `SET app.tenant_id` can stay on a server connection that serves another client next, and the
  next transaction of the same client can run on a connection without it. The transaction-local form above is the
  only one that holds in this mode.
- Statements outside an explicit transaction are each their own transaction. A setting made in one autocommit
  statement is gone for the next. Wrap tenant work in explicit transactions.

## Test lane

- The suite runs as the application role behind the production pooler mode, with `FORCE` on.
- A test runs a tenant query without setting the tenant and expects zero rows.
- A test sets tenant A, commits, and checks that the next transaction on the pool sees no tenant.
- A test inserts a duplicate per-tenant key across two tenants and expects success.
