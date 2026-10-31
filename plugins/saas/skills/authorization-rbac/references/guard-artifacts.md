# Guard artifacts for authorization

Load when writing the authorization matrix, escalation tests or the structural guards. Each artifact turns a rule
from SKILL.md into a check that fails the build.

## Contents

- Authorization matrix
- Grant-path escalation tests
- Owner-all test
- Route inventory test
- Choke-point grep guard
- Deactivation tests
- Catalog coverage test
- Policy arch tests
- Mass-assignment tests
- Token storage test

## Authorization matrix

One dataset-driven test per policy, generated from the catalog. For each ability:

| Actor | Expected |
|---|---|
| owner with zero roles | allow |
| member whose role has the permission | allow |
| member without it | deny (403 on a known in-tenant resource) |
| deactivated member who had it | deny |
| member of another tenant | 404 |

The test fails when the catalog gains an entry that has no matrix row. Build tenants and members through the real
creation path so default roles exist.

## Grant-path escalation tests

For each grant path (role create, role edit, role assignment, invitation, SSO mapping, token mint, connection
create, token rotation):

1. An actor holds a subset S of the catalog.
2. Request a set that adds one permission outside S.
3. Expect the validation error naming that permission, and nothing persisted (row counts and pivots unchanged).
4. Request a set inside S; expect success.

Plus one test for assigning an existing role that contains a permission outside S, and one for adding a permission
to a role the actor holds.

## Owner-all test

- Iterate every catalog permission for an owner with zero roles: all allow.
- Delete every role in the tenant: the owner's effective set still equals the full catalog.

## Route inventory test

List every route in the tenant area. Each must have a policy call, ability middleware or gate. Exceptions sit on an
allowlist with reasons (health checks, public pages). A new route without a check fails the build.

## Choke-point grep guard

With comments stripped, owner comparisons (for example `owner_id ===`) and the active-membership filter appear only
in the effective-permissions service and the membership choke point. Every other hit needs an allowlist entry with a
reason.

## Deactivation tests

One per trigger (manual deactivation, removal, plan downgrade, tenant deletion). Afterwards:

- the member's API tokens are rejected;
- channel authorization returns false;
- cached permissions are empty;
- a job dispatched before deactivation skips and records why.

## Catalog coverage test

Both directions: every catalog entry is enforced somewhere; every checked value is a catalog entry. Stored role
permissions and token abilities are a subset of the catalog.

## Policy arch tests

- Every tenant policy extends the base policy.
- Every ability the code checks has a method on its policy (the Laravel `before()` trap).
- No policy pre-check returns allow for staff.

## Mass-assignment tests

Send `is_admin`, staff flags, `owner_id`, tenant pointers and role IDs through the profile-update form and through
create endpoints. Nothing changes.

## Token storage test

After minting, no column in the token table equals the plaintext, and the hash verifies against it.
