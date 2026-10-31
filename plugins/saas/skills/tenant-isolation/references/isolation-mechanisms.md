# Isolation mechanisms

Load when designing tenancy, adding an ORM global scope, or proposing PostgreSQL row-level security. Explicit
scoping through the tenant relation, enforced by structural guard tests, is always in place. A global scope or RLS
can be added as a second line. The ADR names the second line's failure mode and the guard that covers it.

## The three mechanisms

| Mechanism | How it fails | What catches it |
|---|---|---|
| Explicit scoping through the tenant relation (always) | someone writes a global lookup, a raw query or a join that skips the tenant | probe tests per surface; a structural guard over raw queries and global lookups |
| ORM global tenant scope | raw SQL, joins and query-builder paths skip it; route binding may run before the tenant is bound, so the scope is not active yet; it also shrinks system queries that have no viewer | the same probe tests; restricted-actor tests on system paths; a guard listing every opt-out |
| PostgreSQL row-level security | superusers and `BYPASSRLS` roles always bypass it; the table owner bypasses it unless the table has `FORCE ROW LEVEL SECURITY`; unique, primary-key and foreign-key checks bypass it and can reveal existence; a session-level tenant setting under a transaction pooler reaches the wrong transaction | an RLS test lane that runs as a non-owner role without `BYPASSRLS`; the pooler rules in `stack-postgres-rls.md` |

RLS facts: PostgreSQL docs, Row Security Policies (https://www.postgresql.org/docs/current/ddl-rowsecurity.html,
verified 2026-10-31).

## Choosing

- Explicit scoping keeps every tenant predicate visible in the code that runs it. Reviewers can see it, and the
  guards can count the exceptions.
- A global scope removes repetition, and it also hides the predicate. Add one only with a named opt-out, a guard
  that lists every use of it and of the framework's generic scope removal, and a decision for each system path.
- RLS adds a check the application cannot forget, and it moves part of the security model into database roles and
  connection settings. Adopt it only with the test lane and the pooler check, and keep explicit scoping in place.

## Choosing the tenant source

- A URL segment (`/workspaces/{workspace}/...`), a subdomain, or a token bound to one tenant. Each request names its
  tenant.
- Session state ("current workspace") is a cache of that choice, never the source. Two browser tabs on two
  workspaces otherwise write into whichever was chosen last.
- Whatever the source, membership is checked before the tenant is bound.

## ADR template

```markdown
# ADR: tenant isolation mechanism

Status: proposed | accepted
Date: YYYY-MM-DD

## Decision
Primary mechanism: explicit scoping through the tenant relation. Second line: [none | global scope | RLS].
Tenant source: [URL segment | subdomain | token].

## Failure mode we accept
[For each mechanism, how it fails.]

## Guards that cover it
[Probe tests, structural guard, restricted-actor tests, RLS test lane, pooler check.]

## System paths
[List of paths with no viewer and how each opts out; owner of the list.]

## Consequences
[What reviewers check; what a new tenant table needs.]
```
