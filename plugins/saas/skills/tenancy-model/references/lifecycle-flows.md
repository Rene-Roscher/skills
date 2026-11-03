# Lifecycle flows

Load when building ownership transfer, invitation acceptance, organization deletion and restore, or a project
move. Each flow lists its steps, the checks that run inside the transaction, and the tests.

## Contents

- Invitation acceptance
- Ownership transfer
- Organization deletion, restore and purge
- Moving a project between organizations

## Invitation acceptance

1. Hash the presented token and load the invitation by hash. Unknown, revoked, accepted and expired tokens all
   give the same answer, so the endpoint does not reveal which invitations exist.
2. Require a signed-in user whose verified email equals the invitation email (the default; an ADR can relax it).
3. In one transaction: lock the organization row, re-check status and expiry, ask `plan-entitlements` whether a
   seat is free, re-check that each role to grant is within the inviter's current rights
   (`authorization-rbac`), insert or reactivate the membership, attach roles, set the invitation to accepted.
4. After commit: invalidate the user's organization list and the organization's member caches, audit the event.

Tests: accept twice; accept after expiry; accept when seats are full (refused, invitation stays pending); accept
after the inviter lost the granted role; accept by a user who is already a member (no duplicate row, no extra
roles).

## Ownership transfer

1. Owner requests transfer to an active member, after re-authentication. A pending transfer row stores old owner,
   target and expiry; at most one pending transfer per organization.
2. Target accepts while signed in. Either side can cancel before that.
3. In one transaction: lock the organization row, re-check that the requester is still owner and the target is
   still an active member, set `owner_id`, close the transfer row.
4. Recompute per-owner state for both people: allowances counted per person, the billing contact if it followed
   the owner, owner-scoped caches. Audit with actor, old owner, new owner.
5. Notify both people.

Tests: new owner has every right with zero roles; old owner keeps their roles and loses only owner status;
target removed before accepting makes the acceptance fail; per-owner counters are correct for both people after
the transfer.

## Organization deletion, restore and purge

Deletion (owner only, re-authenticated):

1. Set `deleted_at` and `purge_after`. From this moment the tenant resolver treats the organization as missing.
2. Cancel or schedule the end of the subscription (billing rules in `billing-eu-b2b`).
3. Stop scheduled work: jobs check the organization's state when they run, not only when they were queued.
4. Take public surfaces offline (public pages, custom domains, inbound webhooks answer as if unknown).
5. Notify members; audit.

Restore (owner, inside the window): clear `deleted_at` and `purge_after`, restart scheduled work, bring public
surfaces back. Records keep their public IDs.

Purge (after `purge_after`):

1. Delete in batches, children before parents, per table from a list that a CI check compares with the catalog.
2. Delete the organization's files by exact path or prefix in object storage, rows in analytics stores and search
   indexes, and cache tags.
3. Write a completion record (organization public ID, time, tables and counts) without personal data.
4. Backups age out by their own retention; erasure duties are handled in `gdpr-engineering`.

Tests: during the window members get 404 and jobs exit without side effects; restore brings back every record
with the same public ID; after purge a schema-driven query finds zero rows for the organization; another
organization sharing members is unchanged.

## Moving a project between organizations

1. Preview: list what moves (project, tasks, comments, files), what is detached (project members without a
   membership in the target, integrations and tokens of the source, usage already billed), and whether the
   target's entitlements allow one more project and its size.
2. Authorize: move right in the source and create right in the target, for the same user.
3. In one transaction: lock both organization rows in a fixed order (lower internal ID first) to avoid deadlocks,
   re-check the target's entitlements, rewrite `organization_id` on the project and every child table, detach what
   the preview listed.
4. After commit: move object-storage files to the target prefix (idempotent, retried by a job), update analytics
   and search rows, invalidate both organizations' cache tags, force re-authorization of open realtime
   subscriptions, audit in both organizations.
5. Old URLs: redirect to the new organization path for members of the target, 404 for everyone else.

Tests: no row of the project keeps the old `organization_id`; a target at its project limit refuses before any
row changes; a user with rights in only one of the two organizations gets 403 or 404; two concurrent moves of the
same project do not both succeed.
