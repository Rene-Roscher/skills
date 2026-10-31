# RBAC package or in-house core

Load when someone proposes an RBAC package, or asks why authorization is built in-house. The default is an in-house
core. The argument is ownership of the invariants, not that packages cannot do tenants.

## Questions for the ADR

1. Are roles per tenant, and are role definitions per tenant (each tenant names its own roles)?
2. Can the package express, without a fork: the owner rule, the escalation cap on every grant path, token ability
   subsets, deactivation that removes every right at once?
3. Does it keep an ambient "current team" or "current tenant" in global state? If so, what resets it per request on
   long-lived workers, and per job in queue workers?
4. How does it cache permissions, and how is that cache invalidated on a role edit, on deactivation and across
   tenants?
5. Who audits it, how often does it release, and what does leaving it cost (data model, migrations, call sites)?

## Example: spatie/laravel-permission

Read from the package docs on 2026-10-31. Re-check at the version being compared.

- It has a teams mode: set `'teams' => true` in `config/permission.php` before running the migrations
  (https://github.com/spatie/laravel-permission/blob/main/docs/basic-usage/teams-permissions.md).
- The active team is a global value set with `setPermissionsTeamId($teamId)`, typically in middleware.
- After switching the team, the docs say to unset the user's cached `roles` and `permissions` relations before
  checking roles or permissions.
- For Octane, the docs offer a `register_octane_reset_listener` setting to flush the permission cache on each reset
  cycle "if you find that cache results are stale or crossing over between requests"
  (https://github.com/spatie/laravel-permission/blob/main/docs/advanced-usage/cache.md).
- The package ships its own agent skill, `laravel-permission-development`, for its syntax.

So the package supports team-scoped roles. Weigh against the questions above: the global team ID (question 3), the
relation cache after switching (question 4), and whether the owner rule, the escalation cap and token subsets are
expressible without wrapping every grant path yourself (question 2).

## ADR template

```markdown
# ADR: authorization core

Status: proposed | accepted
Date: YYYY-MM-DD

## Decision
[In-house core | package name and version].

## Answers
1. Per-tenant roles: ...
2. Owner rule, escalation cap, token subsets, deactivation: ...
3. Ambient state and reset per request and per job: ...
4. Permission cache and invalidation: ...
5. Audit, release cadence, exit cost: ...

## Guards that apply either way
Route inventory, owner-all, grant-path escalation tests, deactivation tests, catalog coverage, matrix.
```

The guard tests in this skill run against whichever core is chosen. A package does not remove them.
