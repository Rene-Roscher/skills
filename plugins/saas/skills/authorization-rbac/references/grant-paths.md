# Grant paths and the escalation cap

Load when a feature creates or edits roles, assigns roles, invites members, maps SSO groups, mints tokens, creates
agent or integration connections, or delegates in any other way.

## What counts as a grant path

Any code that can make a principal hold a permission it did not hold before:

- creating a role with permissions;
- editing a role's permissions (everyone holding the role gains them);
- assigning an existing role to a member;
- inviting a member with roles, and accepting the invitation;
- SSO or JIT provisioning that maps groups to roles or sets a default role;
- minting an API token or an agent or integration connection with abilities;
- rotating a token (the new token must not exceed the old subset);
- ownership transfer (its own flow, see below);
- any import, sync or admin script that writes roles, role permissions, memberships or abilities.

## The cap

```text
requested   = permissions the request would grant (for an assigned role: all of the role's permissions)
held        = effective permissions of the actor (owner: the full catalog)
extra       = requested - held
if extra is not empty: reject the whole request, name every entry in extra, persist nothing
```

- Compute `held` with the central effective-permissions function, never at the call site.
- Do not intersect and continue. The caller asked for something specific; trimming it hides the attempt and breaks
  the caller's automation later.
- Default response: 422 with the extras under the permissions field. 403 is the alternative an ADR may choose.
- The audit entry records the attempt with actor, channel and the extras.

## Paths that are easy to miss

- Role assignment. A member with `roles.manage` but without `billing.manage` must not assign a role that contains
  `billing.manage`.
- Editing a role the actor holds. Adding a permission to one's own role is a grant to oneself.
- Invitations accepted later. Check the cap when the invitation is created, and again when it is accepted if the
  inviter's rights may have changed in between.
- SSO mappings. The mapping is configured by an admin; the cap applies when the mapping is saved, capped by the
  admin who saves it.
- Token rotation and re-scoping.

## Ownership transfer

- Only the current owner starts it. The new owner is an active member.
- It is confirmed (by the new owner, or by re-authentication of the current owner, as the product decides) and
  audited.
- The previous owner keeps the roles they hold as a member and loses the owner rule.

## Guard test

A test enumerates the grant paths: routes and services that write role permissions, role assignments, invitations
with roles, token abilities and connection abilities. Each one must call the cap. A new writer that does not fails
the test. Keep the list in the test, reviewed like code.
