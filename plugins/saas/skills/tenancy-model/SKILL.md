---
name: tenancy-model
description: "Designs the tenant hierarchy of B2B SaaS: organization as root tenant, optional projects and teams, memberships (one user, many orgs), owner and ownership transfer, invitations, tenant deletion, moving projects between orgs. Use when adding a tenant level, workspaces, teams or invites, or asked which level owns an entity. Not for query scoping (tenant-isolation) or permissions."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Tenancy model

This skill decides the shape of the tenant tree before any query is scoped: which entity is the tenant, which levels
sit below it, how users join it, who owns it, and how a tenant or a part of it is created, handed over, moved and
removed. Enforcement on every path belongs to `tenant-isolation`, permissions and roles to `authorization-rbac`, ID
formats to `dual-key-identifiers`, plan limits to `plan-entitlements`. The failure it prevents: a hierarchy that
looked simple at signup (one user, one company) and later forces duplicate accounts, orphaned data when a member
leaves, and rows that end up in two tenants after a move.

## Applies when / does not apply

- Applies: choosing the root tenant, adding workspaces, projects or teams, letting one user join several
  organizations, membership and invitation tables, the owner pointer and ownership transfer, deciding which level
  an entity hangs off, tenant segments in URLs, cache keys, queues and channels, deleting or archiving an
  organization, moving a project between organizations, a personal workspace for solo users.
- Does not apply: filtering queries, jobs and caches to the current tenant (`tenant-isolation`), the permission
  catalog, roles and escalation checks (`authorization-rbac`), public ID format (`dual-key-identifiers`), how many
  projects or seats a plan allows (`plan-entitlements`), login, SSO and 2FA, erasure duties and retention periods
  (`gdpr-engineering`).

## Rules

Most important first. Examples use a project tool: organizations (the tenant), projects, tasks, members, teams.

- [invariant] The organization is the root tenant and every tenant-owned entity hangs off exactly one level of it:
  organization-level (subscription, billing contact, members, roles, invitations, API tokens, audit log, domains,
  SSO) or project-level (tasks, files, comments). Tenant data never belongs to a user; a user owns only personal
  things (profile, 2FA, personal notification preferences). Store the creator as `created_by` with a nullable
  reference. Why: data that hangs off a user disappears or breaks when that member leaves or is removed. Test:
  remove the member who created a project; the project, its tasks and the audit trail remain, and `created_by`
  is kept or set to null. Source: reproducible with the test above.
- [invariant] Users are global identities; access to an organization is a membership row, unique per
  `(organization_id, user_id)`, carrying status and roles. One user can be a member of many organizations with
  different roles. No `users.organization_id` or `users.role` column decides access. Why: a tenant column on the
  user forces a second account per company and turns a stale pointer into access. Test: one user in two
  organizations with different roles; removing the membership in A leaves B unchanged, and the next request to A
  returns 404. Source: reproducible with the test above.
- [invariant] The organization a write lands in is the one the user acted on: it travels with the request (path
  segment or token), is checked against an active membership on every request, and a session "current
  organization" is only a default for redirects. Why: with two tabs open on two organizations, a session pointer
  switched in one tab sends the other tab's form into the wrong tenant. Test: load a form in organization A,
  switch to B in a second tab, submit the first form; the record is created in A or the request is rejected,
  never created in B. Source: reproducible with the test above.
- [invariant] When a row carries both a parent reference and `organization_id`, a composite foreign key makes them
  agree: `(project_id, organization_id)` references `projects (id, organization_id)`. Why: the denormalized tenant
  column is what scoping reads, and nothing else stops a task of project P from carrying another tenant's ID after
  a bug or a partial move. Test: insert a task whose `project_id` belongs to organization A with
  `organization_id` B; the database rejects it. Source: reproducible with the test above; DDL in the data-model
  reference.
- [invariant] Exactly one owner per organization, stored as `organizations.owner_id`, always an active member, with
  every right regardless of roles (the check itself lives in `authorization-rbac`). The owner cannot be removed,
  deactivated or leave, and a user account that owns organizations cannot be deleted until each is transferred
  or deleted. Why: an organization without a reachable owner can only be recovered by support editing rows by
  hand. Test: removing the owner's membership and deleting the owner's account both fail with an error that names
  the organizations to transfer first. Source: GitHub docs, "Organization owners have complete administrative
  access to your organization."
  (https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization,
  verified 2026-11-03).
- [invariant] Ownership transfer is a two-step, audited flow: the owner starts it after re-authentication, the
  target must be an active member and accepts explicitly, and acceptance swaps `owner_id` in one transaction.
  The old owner stays a member with their roles. Everything keyed to the owner is recomputed for both people:
  per-owner allowances (such as how many free organizations one person may hold), billing contact, owner-scoped
  caches. Why: an allowance counted per owner otherwise moves with the organization, leaving one person with two
  and the other with none. Test: transfer, then assert the new owner has every right with zero roles, the old
  owner keeps their roles, both owners' per-owner counters are recomputed, and one audit entry records actor,
  old and new owner. Source: reproducible with the test above.
- [invariant] Invitation tokens are random, stored hashed, single use and expiring, bound to one organization and
  one email, with at most one open invitation per `(organization_id, email)`. Acceptance re-checks at accept time:
  status, expiry, seat limit (through `plan-entitlements`) and that the roles to grant are still within the
  inviter's current rights (`authorization-rbac`). Why: limits and the inviter's rights can change in the days
  between invite and accept. Test: accept twice (second fails), accept after expiry (fails), accept when seats
  are full (refused, invitation stays open), accept after the inviter lost the role being granted (refused).
  Source: OWASP Forgot Password Cheat Sheet, tokens are "Single use and expire after an appropriate period."
  (https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html, verified 2026-11-03);
  PostgreSQL partial unique index, "enforces uniqueness among the rows that satisfy the index predicate"
  (https://www.postgresql.org/docs/current/indexes-partial.html, verified 2026-11-03).
- [invariant] A team that is a grouping grants nothing: no authorization check reads team membership unless teams
  are declared a grant source. If teams grant access, they are a role-assignment target computed inside the one
  effective-permission function and covered by its escalation checks, never read ad hoc in one controller. Why:
  a "team" that grants access in one place and nothing elsewhere is a permission system nobody reviews. Test: an
  architecture test that authorization code does not query the team-membership table; removing a user from a
  grouping team changes none of their effective permissions. Source: reproducible with the test above.
- [invariant] Removing a member or deleting an organization never deletes another organization's data, and a
  deleted organization is gone from every surface at once: members get 404, scheduled work for it is skipped,
  public pages go offline, the subscription is cancelled. Physical deletion runs later, in batches, across every
  store (database, object storage, analytics, search, caches), and records completion. Why: a soft-deleted tenant
  whose jobs keep running still sends mail and still bills. Test: delete organization A; its members get 404,
  its queued jobs exit without side effects, organization B (sharing a member) is unchanged; after the grace
  window the purge leaves zero rows for A in every tenant table, checked by a schema-driven query. Source:
  reproducible with the test above.
- [invariant] Moving a project to another organization is one explicit operation: the actor holds the move right
  in the source and the create right in the target, the target's entitlements are checked first, every row of
  the project gets the new `organization_id` in one transaction (composite keys carry children along or make a
  missed table fail), and
  what cannot move (project members who are not members of the target, integrations, API tokens, usage already
  billed) is listed in a preview and detached. Public IDs stay the same, both organizations' caches are
  invalidated, open realtime subscriptions re-authorize, and the move is audited in both organizations. Why: a
  partial move leaves rows of one project in two tenants. Test: move a project with tasks and comments; no row of
  it keeps the old `organization_id`; a target at its project limit refuses; the old URL redirects or returns 404
  as decided. Source: GitHub docs on repository transfer, "All links to the previous repository location are
  automatically redirected to the new location."
  (https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository,
  verified 2026-11-03).
- [default] Add levels only for a need customers have today: start with organization and, if the product groups
  work, projects. Teams and per-project roles come when a customer asks for different rights per project. Trade-off:
  a later level means a migration, in exchange for not scoping every query, key and channel by a level nobody
  uses. Deviate only with an ADR that names this trade-off. Proof: each level has a feature that reads it.
- [default] A solo user's space is an organization with one member, created at signup, not a separate user-owned
  workspace type. Trade-off: one organization row per signup, in exchange for one code path for scoping, billing
  and invitations, and no conversion when the solo user invites a colleague. Deviate only with an ADR that names
  this trade-off. Proof: no query branches on "personal" versus "organization".
- [default] Every tenant-owned table carries `organization_id` directly, even below a project, and composite
  indexes lead with it. Trade-off: one extra column per row and a rewrite on project moves, in exchange for scoping
  without join chains and one index prefix for every tenant query. Deviate only with an ADR that names this
  trade-off. Proof: a schema check that every table with a foreign key to a tenant-owned table has a non-null
  `organization_id`.
- [default] The hierarchy appears the same way everywhere: URLs `/orgs/{org}/projects/{project}/…` with public IDs
  (`dual-key-identifiers`), cache keys and tags `org:{id}` then `org:{id}:project:{id}`, queue payloads with the
  organization key, channel names with public IDs, storage paths `org/{id}/project/{id}/…`. One key builder makes
  them; an organization tag invalidates its projects. Trade-off: longer keys and paths, in exchange for purging or
  moving a subtree by prefix. Deviate only with an ADR that names this trade-off. Proof: an architecture test that
  cache keys and channel names are built only by the builder.
- [default] Roles are organization-scoped. Project-scoped roles, when added, are additive to organization roles,
  computed in the one effective-permission function, and never grant organization-level actions (billing,
  members, deletion). Trade-off: no "admin of project X only" who manages members, in exchange for one place where
  organization power is decided. Deviate only with an ADR that names this trade-off. Proof: a project-role holder
  without organization roles gets 403 on member and billing routes.
- [default] Invitations bind to the invited email: acceptance requires a signed-in user with that verified
  address. Trade-off: a forwarded invitation needs a new invite, in exchange for a link that grants nothing to
  whoever else receives it. Deviate only with an ADR that names this trade-off. Proof: accepting with a different
  verified email is refused.
- [default] Organization deletion has a grace window during which the owner can restore everything with the same
  public IDs; foreign keys to `organizations` use `ON DELETE RESTRICT` and the purge job deletes children in
  batches. Trade-off: a purge job to maintain, in exchange for no single cascading statement over millions of
  rows and a loud failure when a new table is missing from the purge. Deviate only with an ADR that names this
  trade-off. Source: PostgreSQL docs, `RESTRICT` "prevents deletion of a referenced row"
  (https://www.postgresql.org/docs/current/ddl-constraints.html, verified 2026-11-03).

## Procedure

1. Gate: is this a new tenant level, a new tenant-owned entity, a membership or ownership change, or a lifecycle
   operation (delete, restore, move)? If it only scopes an existing query, use `tenant-isolation`.
2. Place each new entity on one level with the ownership question: whose lifecycle and bill does it follow?
3. Schema: `organization_id` on the table, composite foreign key to the parent, index leading with the tenant.
4. Memberships: unique `(organization_id, user_id)`, status column, roles through `authorization-rbac`.
5. Owner flows: owner pointer, transfer with acceptance, guard on account deletion.
6. Invitations: hashed token, expiry, partial unique index, accept-time checks.
7. Lifecycle: soft delete with grace, job and surface shutdown, batched purge across stores, restore test.
8. Moves: preview, entitlement check in the target, single-transaction rewrite, cache and channel refresh, audit.
9. Wire keys, channels and paths through the key builder; add the tests named in the rules.

## Traps

- A `current_organization_id` on the user or session looks like convenience and becomes the tenant decision the
  first time a controller reads it instead of the route.
- A team created "for notifications" acquires a permission check in one controller and is now an unreviewed
  role.
- Invitation acceptance that checks the seat limit only when the invite was sent lets ten pending invites fill
  three seats.
- Per-owner allowances (free organizations per person, trial eligibility) silently move with an organization on
  transfer unless the transfer recomputes both owners.
- Soft-deleting the organization row while its scheduled jobs keep a cached copy: the jobs keep sending mail.
- A project move that updates the projects table and the tasks table but forgets attachments in object storage
  or rows in an analytics store; only a schema-driven check finds the forgotten table.
- `ON DELETE CASCADE` from `users` to memberships is fine; cascading from `users` to tenant data deletes an
  organization's work when one member deletes their account.

## Done when

- Every tenant-owned table has `organization_id`, a composite key to its parent, and a level it belongs to.
- One user can hold memberships in two organizations with different roles, proven by a test.
- Owner removal and owner account deletion are refused; ownership transfer is tested end to end.
- Invitations are hashed, single use, expiring, unique per open email, and re-checked at accept time.
- Deleting, restoring and purging an organization, and moving a project, each have the tests named above.

## References

- [references/data-model.md](references/data-model.md): load when writing migrations for organizations,
  memberships, invitations, teams or project-level tables, or when choosing foreign-key actions.
- [references/lifecycle-flows.md](references/lifecycle-flows.md): load when building ownership transfer,
  invitation acceptance, organization deletion and restore, or moving a project between organizations.

## Sources

- https://docs.aws.amazon.com/whitepapers/latest/saas-architecture-fundamentals/tenant-isolation.html: isolation
  uses tenant context and is separate from authentication and authorization, verified 2026-11-03.
- https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization:
  owners have complete administrative access, verified 2026-11-03.
- https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository: what moves
  with a transferred repository and redirects of old links, verified 2026-11-03.
- https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html: random, stored securely,
  single-use, expiring tokens, verified 2026-11-03.
- https://www.postgresql.org/docs/current/indexes-partial.html: partial unique index, verified 2026-11-03.
- https://www.postgresql.org/docs/current/ddl-constraints.html: `RESTRICT` and `CASCADE` foreign-key actions,
  verified 2026-11-03.
