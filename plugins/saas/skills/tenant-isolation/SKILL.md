---
name: tenant-isolation
description: "Enforces tenant isolation in multi-tenant B2B SaaS on every path data can cross: web, API, background jobs, scheduled tasks, caches, exports and downloads, outbound webhooks and notifications, realtime channels and secondary stores. Covers a tenant context that fails closed and is cleared per request on long-lived workers, resolving resources through the tenant, scoping IDs referenced in input, the trade-offs between explicit scoping, ORM global scopes and PostgreSQL row-level security, system queries that must not be filtered, and cross-tenant probe tests that assert status, unchanged rows and the absence of foreign data. Use when adding a tenant-owned model, endpoint, job, cache key, export, webhook or channel, when introducing a global scope or RLS, or when asked whether customer A can see customer B, about IDOR, or about data leaking between organizations or workspaces. Not for role and permission design (authorization-rbac), ID formats (dual-key-identifiers) or plan limits."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Tenant isolation

This skill keeps one tenant's data away from every other tenant on every path, not only on web requests. It decides
how the tenant is bound, how resources are resolved, what background work may assume, and which tests prove it.
Permissions inside a tenant belong to `authorization-rbac`; the shape of IDs belongs to `dual-key-identifiers`. The
failure it prevents: a lookup, job, cache entry or channel that serves tenant A's data to tenant B without any
error.

## Applies when / does not apply

- Applies: a new tenant-owned model, endpoint, job, scheduled task, listener, cache key, export or download,
  outbound webhook, notification, realtime channel or analytics query; a global scope or row-level security; a
  switch to long-lived workers; a pentest finding about IDOR between tenants.
- Does not apply: designing roles and permissions (`authorization-rbac`), ID formats (`dual-key-identifiers`),
  plan limits and billing (`billing-eu-b2b`), login and 2FA, general query performance, infrastructure HA.

## Rules

Most important first. Examples use a project tool: workspaces (the tenant), projects, tasks, members.

- [invariant] Fail closed without a tenant context: code that reads the current tenant denies or throws when none is
  bound. Never fall back to the user's first tenant, the last used one, or all. Bind the tenant per request from an
  explicit source (URL segment, subdomain or token) after checking active membership, and clear any previous
  binding first, before any early return. Why: on long-lived workers a binding from the previous request survives,
  so a guest or a user without a tenant inherits it. Test: bind workspace A as a previous request would, send a
  guest request and a request from a user with no workspace through the tenant middleware, assert nothing is bound
  afterwards; readers return deny when unbound. Source: OWASP Authorization Cheat Sheet, "Deny by Default"
  (https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html, verified 2026-10-31).
- [invariant] Resolve through the tenant, never globally: load every tenant resource with a query that includes
  the tenant, such as `workspace.projects().where(public_id = ?)`, or a framework feature that scopes child
  bindings to the parent. Do not load globally and check ownership afterwards in each policy method. Why: one
  scoped lookup sends foreign and missing IDs down the same path, so they answer the same by construction; a
  check copied into each method is forgotten in one of them. Test: the probe test below, plus a grep rule that
  flags global lookups by public ID in tenant-facing handlers. Source: OWASP API1:2023, check access "in every
  function that uses an input from the client to access a record"
  (https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization, verified 2026-10-31).
- [invariant] Foreign is missing: with your own tenant in the URL and a valid foreign resource ID, show, update and
  delete return 404, the same as a non-existent ID, on web and API alike. The foreign row stays unchanged and the
  body holds none of its data. Why: a status-only check can be green while data was read or written, and any
  status difference confirms existence. Test: the cross-tenant probe test below. Source: RFC 9110 §15.5.4, a server
  may answer 404 to hide a forbidden resource (https://www.rfc-editor.org/rfc/rfc9110.html, verified 2026-10-31).
- [invariant] Validate referenced IDs inside the tenant: every ID in a request body that points at another resource
  (`project_id`, `member_ids[]`) must exist inside the current tenant and the actor's visible set. Check arrays as
  one set. A foreign ID gives the same validation error as a random one. Why: otherwise a member attaches another
  workspace's project to their own task and reads it later through the relation. Test: post a foreign ID; expect
  the same 422 message as for a random ID and no row or pivot written. Source: reproducible with the test above.
- [invariant] Tenant pointers never come from input: `tenant_id` on rows and current-tenant pointers on users are
  set server-side from the bound context and are not mass-assignable. Why: one form with a mass-assignable pointer
  moves records or users into another tenant. Test: post another workspace's `workspace_id`; the record lands in
  the caller's workspace or the request is rejected. Source: reproducible with the test above.
- [invariant] Jobs carry the tenant explicitly and re-check it when they run: queue jobs, scheduled tasks,
  consumers and listeners receive tenant and resource IDs as scalar parameters, resolve them inside the tenant at
  execution, and re-check that tenant, member and resource are still active. Never read the current tenant from
  ambient state in a job; framework context propagation is for logs and traces, not for data selection. Values that
  depend on the tenant (tax treatment, locale, plan) are passed in or resolved from the tenant explicitly. Why: a
  worker has no request, and delayed jobs run after a member was deactivated; a renewal job that reads the tax
  treatment from ambient state finds no tenant and falls back to domestic VAT for reverse-charge customers. Test: an
  arch rule that job classes do not call the current-tenant accessor; dispatch, deactivate the member, run the
  job, assert it skips with a recorded reason. Source: Laravel 12 docs, Context: data is "dehydrated" into the job
  payload and "hydrated" when the job runs (https://laravel.com/docs/12.x/context, verified 2026-10-31), one example
  of ambient propagation.
- [invariant] Ask of every automatic filter whether the question has a viewer: global scopes, RLS policies and
  visibility sets need a named, greppable opt-out, used for system questions with no viewer (who must be notified,
  does a parent still have children before a cascade, what the scheduler must check, what the tenant is billed
  for). Keep removal loops scoped; filter after aggregation, not before. The structural guard matches every escape
  form, the named opt-out and the framework's generic scope-removal calls. Why: a filter meant for people
  silently shrinks background work, and tests stay green because fixtures bind no restricted actor. Test: for each
  system path, bind a restricted actor and assert the system result is unchanged. Source: reproducible with the
  test above.
- [invariant] Context tenant and target tenant are separate: when a request bound to tenant A acts on tenant B
  (account deletion across every owned tenant, leaving a tenant, staff actions, cross-tenant jobs), rebind or bypass
  explicitly per target. Why: an account deletion bound to one workspace matched nothing in the user's other owned
  workspaces, so their data stayed. Test: the user owns workspaces A and B, context bound to A, delete the account,
  assert B was cleaned up too. Source: reproducible with the test above.
- [invariant] Cache keys are tenant-scoped and viewer-scoped, and invalidation hits the same keyspace: every key or
  tag holding tenant data includes the tenant; values derived from what the actor can see include a fragment of the
  visible set (a short hash of the sorted visible IDs or of the role set). An entry stored under tags is removed by
  flushing the tag, not by a bare key delete. Why: a value computed for one viewer is served to the next. Test: two
  members of one workspace with different visibility, warm as one, read as the other, expect different results; a
  write invalidates the cached read in the same test without time travel. Source: Laravel 12 docs, Cache Tags:
  "Items stored via tags may not be accessed without also providing the tags that were used to store the value"
  (https://laravel.com/docs/12.x/cache, verified 2026-10-31).
- [invariant] Exports and downloads authorize at generation and at download: export jobs select through the tenant
  and the actor's visibility; download endpoints re-check membership and permission when the file is fetched; a
  long random path is not authorization; storage behind a CDN never allows listing. Why: files outlive the
  permission that created them, and a listable bucket turns one leaked path into all of them. Test: a foreign
  member's download returns 404; a member who lost the permission is denied; the bucket policy grants no list action
  to public principals. Source: reproducible with the test above.
- [invariant] Recipients are resolved at one choke point: notifications, outbound webhooks, mails and SMS get
  their recipients from one service that applies the tenant and active-membership rules. Payloads carry only that
  tenant's data and public IDs. Why: several call sites that read the membership relation without the active filter
  kept notifying deactivated members until one choke point replaced them. Test: per channel, a deactivated member
  and a member of another workspace receive nothing. Source: reproducible with the test above.
- [invariant] Realtime channels authorize tenant, active membership and visibility, and their callbacks are tested
  directly: name private and presence channels by public ID, and call the registered authorization callbacks in
  tests for owner, active member, deactivated member, foreign user and restricted member. Why: test setups often use
  a broadcaster whose auth endpoint never runs the callbacks, so an HTTP-level test passes without exercising them.
  Test: the callback tests above. Source: laravel/framework 12.x `NullBroadcaster::auth()` has an empty body
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Broadcasting/Broadcasters/NullBroadcaster.php,
  verified 2026-10-31).
- [invariant] Secondary stores trust only IDs already resolved through the tenant: analytics stores, search indexes,
  object storage and caches have no tenant model of their own. Pass them only IDs from a tenant-scoped lookup in the
  primary store, and make the tenant a required parameter of every query function on them. Why: a metrics query
  keyed by a resource ID from the request skips the primary store's scoping. Test: a foreign resource ID on a
  metrics endpoint returns 404 before the secondary store is queried (assert with a spy or query log). Source:
  reproducible with the test above.
- [invariant] Long-lived workers hold no tenant state: no tenant, user or request state in statics, singletons or
  module globals; per-request memoization lives in request-scoped containers. Framework flush or reset lists contain
  exactly the application's own request-scoped bindings. Why: cross-request bleed is a leak with no error, and
  adding a package's long-lived manager to a flush list broke authentication for the life of each worker, so the
  list must be right in both directions. Test: the leftover-binding test from the first rule, plus a guard test
  that compares container instance bindings against the flush list. Source: reproducible with the test above; stack
  detail in `laravel-production-runtime`.
- [invariant] Cross-tenant probe tests cover every surface: for each tenant resource, probe web, API, export and
  download, webhook configuration and realtime channels with your own tenant in the URL and a valid foreign ID;
  assert 404, an unchanged foreign row re-read from the database, and a body without the foreign record's
  distinctive values. Build both tenants through the real tenant-creation code path. Why: raw factories skip the
  membership and default roles that real tenants have. Test: remove the tenant predicate from one lookup; the
  probes turn red. Source: OWASP API1:2023, "Write tests to evaluate the vulnerability of the authorization
  mechanism. Do not deploy changes that make the tests fail." (verified 2026-10-31).
- [default] An ORM global tenant scope or PostgreSQL row-level security is a second line behind explicit scoping
  and the guard tests, never a replacement for them. Adding one takes an ADR that names the mechanism, its failure
  mode and the guard that covers it. Trade-off: a global scope is bypassed by raw SQL and joins and shrinks system
  queries; RLS is bypassed by superusers, `BYPASSRLS` roles and, without `FORCE ROW LEVEL SECURITY`, the table
  owner; both add a second place where tenancy can fail. Source: PostgreSQL docs, Row Security Policies
  (https://www.postgresql.org/docs/current/ddl-rowsecurity.html, verified 2026-10-31).
- [default] Front-end state that holds tenant data resets the moment the active tenant changes, before the new
  tenant's name renders. Trade-off: a cold cache and refetches on every switch. Deviate only with an ADR that names
  this trade-off. Proof: a component or browser test switches workspaces and asserts no stale values render.

## Procedure

1. Gate: name the tenant boundary for the change and every surface it touches: web, API, job, schedule, cache,
   export, webhook, notification, channel, secondary store.
2. Binding: the entry point clears the old binding, binds from an explicit source after a membership check, and
   fails closed.
3. Lookups: every resource resolves through the tenant; every referenced ID in input is validated inside it.
4. Writes: tenant pointers come from the context, never from input.
5. Background work: scalar tenant and resource IDs in, resolve and re-check at execution, no ambient reads.
6. Filters: for each automatic filter on the path, decide viewer or system; system paths use the named opt-out and
   appear in the guard's allowlist with a reason.
7. Caches, exports, recipients, channels, secondary stores: apply the rules above.
8. Tests: probe tests per surface, leftover-binding test per entry point, restricted-actor tests per system path.
9. If the change adds a global scope or RLS, write or update the ADR first.

## Traps

- Route binding can run before the middleware that binds the tenant, so a global scope is not active yet when the
  model is resolved.
- Scoped child bindings constrain which child is found. They do not check that the actor may use the parent.
- A status-only probe test passes while the foreign row was updated.
- Fixtures built with raw factories have no memberships or default roles, so tests pass against a tenant shape
  production never has.
- A tenant-scoped cache key without a viewer fragment serves one member's numbers to another.
- A cache entry written with tags and deleted by bare key is never deleted.
- A test broadcaster that skips channel authorization makes channel tests pass without running the callbacks.
- RLS with the application connecting as the table owner filters nothing unless the table has
  `FORCE ROW LEVEL SECURITY`.
- Under a transaction-mode connection pooler, a session-level `SET` of the tenant stays on a server connection that
  the pooler hands to other clients without a reset, and the next transaction may land on another connection.
  Details in the RLS reference.

## Done when

- Every entry point that binds a tenant has a leftover-binding test and fails closed.
- Every tenant resource has probe tests on each surface, asserting status, unchanged row and absent foreign data.
- Every job touched takes scalar tenant IDs and re-checks at execution.
- Every system path under an automatic filter uses the named opt-out, is listed in the guard, and has a
  restricted-actor test.
- Cache keys carry tenant and viewer fragments; writes invalidate through the same keyspace.
- Channel callbacks are tested directly.
- An ADR exists for any global scope or RLS.

## References

- [references/isolation-mechanisms.md](references/isolation-mechanisms.md): load when designing tenancy, adding a
  global scope, or proposing RLS; holds the ADR template.
- [references/system-queries.md](references/system-queries.md): load when writing code that runs with no viewer
  (scheduler, notifications, cascades, billing counts) under an automatic filter.
- [references/async-caches-channels.md](references/async-caches-channels.md): load when writing jobs, caches,
  exports, webhooks, notifications or realtime channels.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding a tenant resource or a new
  surface and writing probe tests, the structural guard or the leftover-binding tests.
- [references/stack-laravel.md](references/stack-laravel.md): load when the project uses Laravel.
- [references/stack-postgres-rls.md](references/stack-postgres-rls.md): load when adopting or reviewing PostgreSQL
  row-level security, including behind a connection pooler.

## Sources

- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html: deny by default, verified
  2026-10-31.
- https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization: object-level checks and
  tests that block deploys, verified 2026-10-31.
- https://www.rfc-editor.org/rfc/rfc9110.html: §15.5.4, 404 to hide a forbidden resource, verified 2026-10-31.
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html: default deny, owner, `BYPASSRLS`, `FORCE`,
  referential integrity checks, verified 2026-10-31.
- https://www.postgresql.org/docs/current/functions-admin.html: `set_config` with `is_local`, verified 2026-10-31.
- https://www.pgbouncer.org/features.html: `SET`/`RESET` not supported in transaction pooling, verified 2026-10-31.
- https://www.pgbouncer.org/config.html: in transaction pooling `server_reset_query` is not used and each
  transaction may get a different session state, verified 2026-10-31.
- https://laravel.com/docs/12.x/routing: scoped bindings, verified 2026-10-31.
- https://laravel.com/docs/12.x/cache: cache tags, verified 2026-10-31.
- https://laravel.com/docs/12.x/context: context in queued jobs, verified 2026-10-31.
- https://github.com/laravel/framework/blob/12.x/src/Illuminate/Broadcasting/Broadcasters/NullBroadcaster.php:
  empty `auth()`, verified 2026-10-31.
