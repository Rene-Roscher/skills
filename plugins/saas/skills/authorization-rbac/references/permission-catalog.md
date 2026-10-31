# Permission catalog

Load when adding, renaming or removing a permission, or when generating frontend types from the catalog.

## Shape

- One typed list, for example a PHP backed enum, a TypeScript `as const` object or a Go set of constants.
- Values are `domain.action`: `bookings.view`, `bookings.create`, `bookings.cancel`, `rooms.manage`,
  `members.invite`, `roles.manage`, `tokens.manage`, `billing.manage`, `reports.export`.
- Each entry has a label and a group for the role editor, kept next to the entry.
- Privileged sight and bypasses are entries too (`bookings.view_all`, `approvals.bypass`), never booleans on roles.

## Adding a permission

1. Add the catalog entry with label and group.
2. Enforce it: a policy method, gate or route middleware that references the catalog member.
3. Decide which default roles get it, and seed it through the real tenant-creation path. Existing tenants get it
   through a data migration only if the product decision says so; otherwise only the owner has it until someone
   grants it.
4. Regenerate the frontend types and the token ability list from the catalog.
5. The matrix test picks up the new ability; add its row if the matrix is not fully generated.

## Renaming or removing

- A rename is a data migration over stored role permissions and token abilities, in the same release as the code.
- A removal drops the value from stored roles and tokens and from the catalog. Leave no orphan values in storage.
- Check integrations: a token minted with the old value must keep working (renamed) or be reported to the owner
  (removed).

## Coverage test

Run in CI, in both directions:

- Every catalog entry is referenced by at least one policy, gate or route middleware. An entry nobody enforces is
  something admins grant that does nothing.
- Every permission value used in a check exists in the catalog. String literals at check sites fail the test.
- Every stored role permission and token ability is a catalog value (a query over the seeded test database, or a
  database CHECK constraint where the engine supports one).

## Frontend

- Generate a type from the catalog so frontend checks are typed.
- The server sends the member's effective permission list, computed by the central function. The frontend uses it
  to hide controls. It is never the control.
