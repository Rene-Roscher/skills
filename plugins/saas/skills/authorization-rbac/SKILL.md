---
name: authorization-rbac
description: "Designs and reviews server-side authorization for multi-tenant SaaS: one typed permission catalog, custom roles per tenant, an owner with every right, scoped API tokens, and no escalation on any grant path. Use when touching policies, gates, permissions, roles, invitations, API tokens or admin flags, or asked who can do X or about escalation. Not for data scoping (tenant-isolation) or login."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Authorization and RBAC

This skill decides who may do what inside a tenant, and how permissions are handed out without anyone gaining more
than they hold. RBAC answers "may this member perform this kind of action in this tenant". Which objects a member
reaches inside the tenant, and the fact that other tenants' objects do not exist for them, belong to
`tenant-isolation`. OWASP recommends attribute- and relationship-based checks over pure RBAC; this skill keeps RBAC
for capabilities and leaves object scoping to that skill. The failure it prevents: a delegated admin, a token or a
deactivated member holding rights nobody meant to give.

## Applies when / does not apply

- Applies: policies, gates and route authorization; adding or renaming a permission; role editors; role
  assignment; invitations with roles; SSO group-to-role mapping; API tokens, agent or integration connections;
  admin or staff flags; deactivation and removal of members; ownership transfer; frontend permission checks; a
  proposal to adopt an RBAC package.
- Does not apply: filtering data by tenant or object visibility (`tenant-isolation`), login, password reset,
  sessions and 2FA, ID formats (`dual-key-identifiers`), Kubernetes or cloud IAM, CI token permissions
  (`github-actions-hardening`), encryption between services (`service-boundaries`).

## Rules

Most important first. Examples use a booking system: bookings, rooms, members, permissions such as
`bookings.cancel`.

- [invariant] Authorize on the server, on every request, for the specific action and object: every route, job
  trigger and channel subscription runs a server-side check. Frontend checks only hide buttons. Why: client checks
  are bypassed by calling the endpoint. Test: a route inventory test fails when a tenant route has no policy call,
  ability gate or authorization middleware (allowlist with reasons); per mutating route, a member without the
  permission is denied and the row is unchanged. Source: OWASP Authorization Cheat Sheet: "Developers must never
  rely on client-side access control checks."
  (https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html, verified 2026-10-31).
- [invariant] Deny by default and fail closed: no tenant context, an unknown ability, a missing or deactivated
  membership, and an unknown permission string all evaluate to deny. An exception inside the check never turns into
  allow. Why: authorization bugs that fail open are silent. Test: a unit test per deny branch of the central check,
  including "no tenant bound". Source: OWASP Authorization Cheat Sheet, "Deny by Default" (verified 2026-10-31).
- [invariant] No privilege escalation on any grant path, and reject rather than trim: every path that hands out
  permissions is capped at the actor's own effective permissions (owner: all). That covers creating or editing a
  role, assigning an existing role (which grants all of its permissions), inviting with roles, SSO or JIT default
  roles, minting API tokens, creating agent or integration connections, and any delegation. A request containing
  permissions the actor lacks is rejected as a whole, naming the extra permissions; nothing is persisted. Why: without
  the cap a delegated roles admin mints owner power; a silent intersection leaves the user believing the token can
  do X and hides the attempt from the audit trail. Test: per grant path, an actor with a subset requests a superset,
  gets a validation error listing the extras, and nothing is written; a request within the subset succeeds. A guard
  test enumerates grant paths and fails when a new one lacks the cap. Source: OWASP Authorization Cheat Sheet,
  "Enforce Least Privileges" (verified 2026-10-31).
- [invariant] The owner always has every right and cannot be locked out: the central check grants the tenant's
  owner every permission before it looks at roles. Removing or editing roles never reduces the owner's rights.
  Changing the owner is a separate, audited ownership-transfer flow. Why: an owner who edits their own roles must not
  lock the tenant out, and support should never restore access by hand. Test: iterate every catalog permission for
  an owner with zero roles and expect allow; delete all roles and assert the owner's effective set equals the full
  catalog. Source: reproducible with the test above.
- [invariant] One function computes effective permissions, and everything calls it: owner gets all, an inactive
  member gets none, otherwise the union of roles. Permission checks, grant caps, token minting, the UI's permission
  list and channel authorization all call this function. Why: every copy of "owner gets all" or "inactive gets
  nothing" drifts on its own; several readers that skipped the active condition kept serving deactivated members.
  Test: a grep guard that owner comparisons and the active-membership filter appear only in the permission service
  and the membership choke point (allowlist with reasons). Source: reproducible with the test above.
- [invariant] Privileged sight is a permission, not a flag: capabilities such as "sees every booking regardless of
  visibility", "manages billing" or "bypasses approval" are catalog entries, never booleans on the role or user.
  Why: the escalation cap compares permission sets, so a boolean on the role sits outside it and any role editor can
  set it. Test: a roles admin without the bypass permission creates a role that includes it and is rejected.
  Source: reproducible with the test above.
- [invariant] Privilege-bearing fields are never mass-assignable: staff or admin flags, owner pointers, tenant
  pointers and role assignments are set only in trusted code paths. Why: one self-service form that bulk-fills
  request input grants admin. Test: send the fields through the profile-update form and through create; nothing
  changes. Source: reproducible with the test above; syntax in the framework docs.
- [invariant] Deactivation and removal revoke everything at one choke point: deactivating or removing a member, by
  hand or automatically (plan downgrade, tenant deletion), runs one method that revokes tokens and connections the
  member minted, flushes permission caches, ends realtime authorization and removes scheduled duties. Delayed work
  re-checks membership when it runs. Why: a downgrade path that updated the membership row directly left the
  member's API token valid. Test: per trigger, afterwards the token is rejected, channel auth returns false, cached
  permissions are empty, and a job dispatched before deactivation skips with a recorded reason. Source: reproducible
  with the test above.
- [invariant] Invalidate permission caches explicitly on every write to roles, role permissions, memberships or
  ownership, through the same keyspace they were written to. A TTL is not invalidation. Why: with a five-minute TTL a
  removed admin stays admin for five minutes. Test: change a role and check the effect in the same test without
  moving the clock. Source: reproducible with the test above.
- [invariant] Status codes do not leak: a resource in another tenant returns 404 (owned by `tenant-isolation`); a
  known resource inside the actor's tenant without the permission returns 403; a grant above the actor's permissions
  is a validation error. Error bodies never echo the target's data. Why: inside the tenant the member already knows
  the resource exists; across tenants a 403 confirms existence. Test: one test per failure class. Source: RFC 9110
  §15.5.4, 404 may hide a forbidden resource (https://www.rfc-editor.org/rfc/rfc9110.html, verified 2026-10-31).
- [invariant] API tokens are tenant-owned, hashed and least-privilege: a token belongs to the tenant, carries an
  explicit permission subset chosen at mint time and capped like any grant, and is checked per route by one ability
  check that every pre-route shortcut (idempotent replay, cached responses) also calls. Store only a hash, show the
  plaintext once, support expiry and rotation, and record the token's public ID as the channel in audit entries. Why:
  a replay path that skips the ability check keeps serving an ability that was removed. Test: a token without the
  ability gets 403; replaying an idempotent request after the ability was removed gets 403; the database holds only
  the hash. Source: reproducible with the test above.
- [default] An escalating grant request returns 422 and names the offending permissions. Trade-off: 403 is the
  other defensible choice; 422 says the actor may use the endpoint but this content cannot be processed, and it
  lets clients show the field error. Deviate only with an ADR that names this trade-off. Source: RFC 9110
  §15.5.21: 422 means the syntax is correct "but it was unable to process the contained instructions"
  (https://www.rfc-editor.org/rfc/rfc9110.html, verified 2026-10-31).
- [default] The owner is stored on the tenant (`owner_id`), not as a role. Trade-off: one more column and a
  separate transfer flow, in exchange for an owner rule that no role edit can touch. Deviate only with an ADR that
  names this trade-off. Proof: the owner-all test passes with every role deleted.
- [default] Token prefixes per credential class (user token, integration connection) so secret scanners can match
  them. Trade-off: the prefix reveals the token class to anyone who sees it. Deviate only with an ADR that names
  this trade-off. Proof: a test asserts each class's prefix and a secret-scanning rule matches it.
- [default] Decide in an ADR what happens to a token when its creator is demoted: a frozen tenant service account
  keeps its subset, a delegated credential is effective as token subset ∩ creator's current permissions. In both
  models, a demotion below the token's subset revokes or flags the token for an owner decision. Trade-off: frozen
  tokens keep automation running and outlive the creator's trust; delegated tokens break automation on demotion.
  Deviate only with an ADR that names this trade-off. Proof: demote the creator; the token is revoked, narrowed or
  flagged as the ADR says.
- [default] One typed permission catalog: an enum or equivalent typed list with `domain.action` values. Checks
  reference catalog members, never string literals; stored role permissions are validated against it; token
  abilities and frontend types are generated from it. Trade-off: renaming a permission becomes a data migration over
  stored roles. Deviate only with an ADR that names this trade-off. Proof: a coverage test in both directions (every
  catalog entry is enforced somewhere, every checked value is in the catalog) and stored role permissions are a
  subset of the catalog.
- [default] Roles are per tenant and additive: each tenant defines its roles, effective permissions are the union,
  groups carry no permissions unless the model says so, and default roles are seeded through the real
  tenant-creation path. Trade-off: no deny rules, so an exception means a new role. Deviate only with an ADR that
  names this trade-off. Proof: a test of union semantics on fixtures built through the real creation path.
- [default] Own the authorization core in-house. If a package is proposed, decide in an ADR with these questions:
  are roles per tenant; can it express the owner rule, the escalation cap, token subsets and deactivation without a
  fork; does it keep an ambient "current team" that must be reset per request on long-lived workers; who audits it
  and what does leaving it cost. Trade-off: you write and test the core yourself. Deviate only with an ADR that names
  this trade-off. Source: OWASP Authorization Cheat Sheet: "Do not let the capabilities of any library, platform,
  or framework guide your authorization requirements." (verified 2026-10-31).
- [default] All tenant policies extend one base policy whose pre-check denies when no tenant is bound and denies a
  route-bound subject outside the tenant or the actor's visible set. Platform staff use a separate admin surface or
  audited impersonation, never a pre-check that returns allow. Trade-off: a policy hierarchy every policy must join.
  Deviate only with an ADR that names this trade-off. Source: Laravel 12 docs, Policy Filters: "The `before` method
  of a policy class will not be called if the class doesn't contain a method with a name matching the name of the
  ability being checked." (https://laravel.com/docs/12.x/authorization, verified 2026-10-31), so every checked
  ability needs a method.
- [default] Audit every grant, revoke, role edit, token mint, rotation and revocation, and ownership transfer with
  actor, channel (web, API, token ID, agent) and the before and after sets. Guards and duplicate checks read
  synchronous columns such as `created_by`, never an audit log written asynchronously. Trade-off: synchronous columns
  duplicate part of the audit data. Deviate only with an ADR that names this trade-off. Proof: with a faked queue,
  the guards still work, which shows they do not depend on audit rows.
- [default] Generate the authorization test matrix from the catalog: per ability, owner with zero roles (allow),
  member with the permission (allow), member without (deny), deactivated member (deny), member of another tenant
  (404). Trade-off: a slower suite as the catalog grows. Deviate only with an ADR that names this trade-off. Proof:
  the matrix test fails when the catalog gains an entry without a matrix row.

## Procedure

1. Gate: list the grant paths and checks the change touches. Any new way to hand out permissions goes through the
   escalation cap before anything else.
2. Catalog: add or change catalog entries; update stored roles by migration on rename or removal.
3. Checks: every new route, job trigger and channel calls the central check with a catalog member.
4. Policies: extend the base policy; add a method for every ability checked.
5. Grants: cap at the actor's effective permissions; reject the whole request with the extras named.
6. Lifecycle: deactivation, removal and demotion go through the choke point; caches invalidate on write.
7. Tokens: subset capped at mint, hash stored, ability checked on every path including replays.
8. Tests: the matrix, escalation tests per grant path, owner-all, deactivation per trigger.
9. Frontend: hide what the member cannot do, using the permission list from the central function. The server
   check stays the control.

## Traps

- An intersection that silently drops permissions looks friendly and hides an escalation attempt.
- Assigning an existing role is a grant. A cap on role editing alone leaves role assignment open.
- A boolean such as `sees_all` on the role sits outside every permission-set comparison.
- A downgrade or cleanup job that updates memberships directly skips token revocation.
- A policy pre-check that returns allow for staff makes every policy test pass for staff accounts and hides scoping
  bugs.
- In Laravel, a policy with no method for the checked ability never runs `before()`.
- Idempotent replay and response caches can answer before the ability check runs.
- Guards that read an audit log written by a queue pass in tests (synchronous queue) and never fire in production.
- A package's ambient "current team" survives between requests on long-lived workers unless it is reset.

## Done when

- Every tenant route, job trigger and channel has a server-side check; the route inventory test is green.
- Every grant path is capped and has an escalation test; the grant-path guard lists them all.
- The owner-all test passes with zero roles and after deleting every role.
- Deactivation tests pass for each trigger: tokens, caches, channels, delayed jobs.
- The catalog coverage test passes in both directions, and the matrix covers every ability.
- Tokens store only hashes, and replay paths run the ability check.

## References

- [references/permission-catalog.md](references/permission-catalog.md): load when adding, renaming or removing a
  permission, or generating frontend types.
- [references/grant-paths.md](references/grant-paths.md): load when a feature creates roles, assigns roles, invites,
  maps SSO groups, mints tokens or creates integrations.
- [references/api-tokens.md](references/api-tokens.md): load when designing or changing tokens, agent or integration
  connections, service accounts, rotation or demotion handling.
- [references/package-vs-custom.md](references/package-vs-custom.md): load when someone proposes an RBAC package or
  asks why RBAC is in-house; holds the ADR template.
- [references/stack-laravel-policies.md](references/stack-laravel-policies.md): load when the project uses Laravel
  policies and gates.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when writing the authorization matrix,
  escalation tests or the structural guards.

## Sources

- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html: least privilege, deny by default,
  no client-side checks, review chosen tools, ABAC and ReBAC over RBAC, verified 2026-10-31.
- https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization: object-level checks,
  verified 2026-10-31.
- https://www.rfc-editor.org/rfc/rfc9110.html: §15.5.4 (404 hides a forbidden resource) and §15.5.21 (422), verified
  2026-10-31.
- https://laravel.com/docs/12.x/authorization: policy filters and `denyAsNotFound()`, verified 2026-10-31.
- https://github.com/spatie/laravel-permission/blob/main/docs/basic-usage/teams-permissions.md: teams mode and
  `setPermissionsTeamId()`, verified 2026-10-31.
