# Retrofitting public IDs

Load when an existing API, page or integration already exposes sequential IDs. The move is expand/contract: add the
new key next to the old one, move every reader and writer, then remove the old path.

## Steps

1. Inventory. List every place the internal key leaves the system: routes, JSON fields, page props, cursors,
   `Location` headers, exports, mails, webhooks, channel names, client SDKs and third-party integrations that stored
   the numeric ID. Run the leak guard in `report` mode over the suite to find the HTTP ones.
2. Expand the schema. Add `public_id` as nullable, with no constraint yet.
3. Backfill in batches. Fill rows in primary-key ranges of a few thousand, each batch in its own short transaction,
   with the same generator the application uses. New rows get an ID at creation from the first deploy on.
4. Add the unique constraint without a long lock. On PostgreSQL, build the index with
   `CREATE UNIQUE INDEX CONCURRENTLY`, then attach it with `ALTER TABLE ... ADD CONSTRAINT ... UNIQUE USING INDEX`.
   The PostgreSQL docs describe this as the way to add a constraint "without blocking table updates for a long time"
   (https://www.postgresql.org/docs/current/sql-altertable.html, verified 2026-10-31). `CREATE INDEX CONCURRENTLY`
   cannot run inside a transaction block (https://www.postgresql.org/docs/current/sql-createindex.html, verified
   2026-10-31), so the migration must not wrap it in one. After the backfill, set `NOT NULL`. On a large table,
   add `CHECK (public_id IS NOT NULL) NOT VALID`, validate it, then set `NOT NULL`: a valid CHECK constraint that
   proves no NULL can exist lets PostgreSQL skip the table scan (same ALTER TABLE page, verified 2026-10-31).
5. Switch writers and readers. Serializers emit the public ID under `id`; reference fields emit referenced public
   IDs; route binding uses `public_id`; cursors switch to a non-internal sort key.
6. Deprecation window, only if the business accepts the exposure. Old numeric routes may keep resolving on read-only
   paths for a fixed period, recorded in an ADR with the end date. They answer with a redirect or a deprecation
   header that names the public-ID URL. Writes accept only public IDs from day one.
7. Contract. Remove numeric routes, numeric fields and the compatibility code. Switch the leak guard from `report` to
   `fail`.

## Checks

- A test that old numeric routes stop resolving after the window (404, like any other missing ID).
- A test that every row has a public ID after the backfill (`count(*) WHERE public_id IS NULL` is 0) before the
  `NOT NULL` step.
- The leak guard is in `fail` mode in CI before the work is called done.

## Integrations that stored numeric IDs

- Outbound webhooks: send both fields for one deprecation window only if receivers need it, and say in the payload
  documentation which one goes away.
- Imports from partners: keep their identifiers in a tenant-scoped `external_id` column, never in `public_id`.
- Client SDKs: release a version that reads `id` as a string before the server switches the type.
