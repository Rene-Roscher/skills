# Data model

Load when writing migrations for the tenant tree. PostgreSQL syntax; the example is a project tool. Public IDs
follow `dual-key-identifiers`; only the tenant columns and constraints are shown here.

## Contents

- Organizations and memberships
- Invitations
- Teams as a grouping
- Project-level tables with a composite key
- Foreign-key actions
- Schema checks

## Organizations and memberships

```sql
CREATE TABLE organizations (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id   varchar(21) NOT NULL UNIQUE,
    owner_id    bigint NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    name        text NOT NULL,
    deleted_at  timestamptz,          -- soft delete starts the grace window
    purge_after timestamptz           -- set together with deleted_at
);

CREATE TABLE memberships (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id bigint NOT NULL REFERENCES organizations (id) ON DELETE RESTRICT,
    user_id         bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    status          text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deactivated')),
    joined_at       timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, user_id)
);
CREATE INDEX ON memberships (user_id);   -- "which organizations is this user in"
```

The owner is also a membership row. Keep that true in the transfer and creation code, and check it in a test:
for every organization, a membership with `user_id = owner_id` and status `active` exists. `owner_id` uses
`RESTRICT`, so deleting an owner's user row fails in the database even if the application guard is skipped.

Role assignments reference `memberships.id`, not `users.id`, so removing the membership removes the roles in that
organization and nowhere else.

## Invitations

```sql
CREATE TABLE invitations (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id bigint NOT NULL REFERENCES organizations (id) ON DELETE RESTRICT,
    email           citext NOT NULL,
    token_hash      bytea NOT NULL UNIQUE,      -- hash of the random token; the token is only in the mail
    invited_by      bigint REFERENCES users (id) ON DELETE SET NULL,
    status          text NOT NULL CHECK (status IN ('pending', 'accepted', 'revoked', 'expired')),
    expires_at      timestamptz NOT NULL,
    accepted_at     timestamptz
);
-- one open invitation per email and organization; accepted and revoked rows stay as history
CREATE UNIQUE INDEX invitations_one_open ON invitations (organization_id, email) WHERE status = 'pending';
```

Roles to grant live in a child table (`invitation_roles`) with real foreign keys, so a deleted role cannot be
granted later from a stale JSON array. `citext` needs the extension; a lower-cased `text` column with a check
works too.

## Teams as a grouping

```sql
CREATE TABLE teams (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id bigint NOT NULL REFERENCES organizations (id) ON DELETE RESTRICT,
    name            text NOT NULL,
    UNIQUE (organization_id, name),
    UNIQUE (id, organization_id)
);
CREATE TABLE team_members (
    team_id         bigint NOT NULL,
    membership_id   bigint NOT NULL REFERENCES memberships (id) ON DELETE CASCADE,
    organization_id bigint NOT NULL,
    PRIMARY KEY (team_id, membership_id),
    FOREIGN KEY (team_id, organization_id) REFERENCES teams (id, organization_id) ON DELETE CASCADE
);
```

Team rows point at memberships, so leaving the organization leaves its teams. If teams become a grant source,
that is a decision for `authorization-rbac`, recorded in an ADR, and the effective-permission function is the only
reader.

## Project-level tables with a composite key

```sql
CREATE TABLE projects (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id bigint NOT NULL REFERENCES organizations (id) ON DELETE RESTRICT,
    created_by      bigint REFERENCES users (id) ON DELETE SET NULL,
    UNIQUE (id, organization_id)            -- target of the composite keys below
);

CREATE TABLE tasks (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id bigint NOT NULL,
    project_id      bigint NOT NULL,
    created_by      bigint REFERENCES users (id) ON DELETE SET NULL,
    FOREIGN KEY (project_id, organization_id)
        REFERENCES projects (id, organization_id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX ON tasks (organization_id, project_id);
```

`ON UPDATE CASCADE` on the composite key lets a project move rewrite `projects.organization_id` and have the
children follow inside the same transaction. Without it, update children first with the constraint deferred
(`DEFERRABLE INITIALLY DEFERRED`), or the move fails halfway. Choose one and test the move.

## Foreign-key actions

| Reference | Action | Reason |
|---|---|---|
| tenant table → `organizations` | `RESTRICT` | the purge job deletes children in batches; a forgotten table fails loudly |
| child → parent inside a project | `RESTRICT` or `CASCADE` | `CASCADE` only for small, bounded trees |
| `memberships.user_id` → `users` | `CASCADE` | a deleted account leaves every organization |
| `created_by`, `invited_by` → `users` | `SET NULL` | tenant data survives the person |
| `organizations.owner_id` → `users` | `RESTRICT` | no organization without an owner |

## Schema checks

Run these in CI against a migrated database:

- every table that has a foreign key to a tenant-owned table has a non-null `organization_id`;
- every such table has a composite foreign key that includes `organization_id`;
- no foreign key from a tenant table to `users` uses `CASCADE`;
- every tenant table appears in the purge job's table list (compare the catalog with the list).
