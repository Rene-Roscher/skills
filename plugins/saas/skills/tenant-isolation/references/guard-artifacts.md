# Guard artifacts for tenant isolation

Load when adding a tenant resource or a new surface, or when writing probe tests, the structural guard or the
leftover-binding tests. Each artifact turns a rule from SKILL.md into a check that fails the build.

## Contents

- Cross-tenant probe kit
- Leftover-binding tests
- Structural guard
- Restricted-actor fixtures
- Job arch rule
- Cache tests
- Channel callback tests
- Mass-assignment test
- RLS test lane

## Cross-tenant probe kit

A dataset-driven helper, for example `probeForeign(resource, surfaces)`.

1. Build two tenants through the real tenant-creation code path, so both have memberships and default roles.
2. Create the resource in tenant B and record a distinctive value (a name such as `zz-foreign-marker`).
3. As a member of tenant A, with tenant A in the URL and B's resource ID:
   - show, update and delete on web and API;
   - export or download of the resource;
   - webhook configuration that references it;
   - subscription to its realtime channel.
4. Assert for each probe:
   - status 404 (the same as for a random well-formed ID);
   - the foreign row, re-read from the database, is unchanged;
   - the response body does not contain the distinctive value.
5. Mutation check, once: remove the tenant predicate from one lookup and confirm the probes turn red.

Request-body references get their own probe: post B's resource ID as `project_id` and assert the same validation
error as for a random ID, with no row or pivot written.

## Leftover-binding tests

One per entry point that binds a tenant (web middleware, API token middleware, queue job middleware, console
commands that act per tenant).

1. Bind tenant A as a previous request would have.
2. Run a guest request, then a request from a user with no tenant, through the entry point.
3. Assert nothing is bound afterwards and that the tenant readers return deny.

## Structural guard

A test that scans source files with comments stripped:

- raw SQL and query-builder joins that touch tenant tables;
- global lookups by public ID in tenant-facing handlers;
- named opt-outs of automatic filters;
- the framework's generic scope-removal calls.

Each hit must be on an allowlist with a reason. Pin the total count, so adding an exception is a reviewed change
and removing one updates the pin.

## Restricted-actor fixtures

A test trait that binds a restricted viewer (sees one of three projects) before running scheduler, notification,
cascade and billing code. Each system path runs once unbound and once restricted; the results are equal.

## Job arch rule

Job, listener and command classes do not call the current-tenant accessor. An arch test (or a grep over those
directories) fails on any call.

A behaviour test per job: dispatch, deactivate the member or schedule the tenant for deletion, run the job, assert
it skipped and recorded why.

## Cache tests

- Two members of one tenant with different visible sets: warm as one, read as the other, expect different values.
- A write invalidates the cached read in the same test, without moving the clock.
- A lint or test that every cache key built for tenant data contains the tenant fragment.

## Channel callback tests

Fetch the registered callback for each channel and call it for: owner, active member, deactivated member, member of
another tenant, restricted member who cannot see the resource. Assert true only for the first two.

## Mass-assignment test

Create and update through the public endpoints with another tenant's `workspace_id` in the body. The record stays in
the caller's tenant, or the request is rejected.

## RLS test lane

Only if RLS is adopted. Run the suite as an application role that is not the table owner and has no `BYPASSRLS`,
with `FORCE ROW LEVEL SECURITY` on every tenant table, behind the same pooler mode production uses. A query that
returns rows without a tenant setting fails the lane.
