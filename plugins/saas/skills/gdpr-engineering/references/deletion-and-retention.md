# Deletion and retention

Review-ready draft, not legal advice. Scope: EU (GDPR Art. 5(1)(e), 17), https://eur-lex.europa.eu/eli/reg/2016/679/oj
(verified 2026-10). German retention periods are in the separate German reference of this skill.

## Erasure flow

1. Resolve the scope: one person (Art. 17 request, account deletion) or one tenant (contract end).
2. Walk the inventory, not the model graph. Every `sources.tables` column and `storage_prefixes` entry for the
   affected data categories is in scope.
3. For each location, choose delete, scrub (overwrite the personal fields, keep the row) or retain under a legal
   duty (restrict access, clear what the duty does not need).
4. Delete object-storage prefixes by exact path. Where listing is not permitted, keep the generated paths in the
   database so the erasure can address each file.
5. Evict caches and remove search-index documents for the subject.
6. Write an erasure record without the erased data (subject's public ID or a hash, time, scope, outcome).

## Places that keep copies

- Denormalised snapshots: delivery logs, sent-message archives, notification histories, audit labels.
- Generated files: exports, imports, PDFs, thumbnails.
- Caches, search indexes, analytics stores with their own retention.
- Queued jobs whose payload carries the data.
- Backups: erasure does not rewrite them. Document the rotation window and make sure a restore re-applies
  erasures recorded since the backup was taken.

## Foreign keys

- References to a person use `ON DELETE SET NULL` (keep the business record) or `ON DELETE CASCADE` (the row
  exists only for that person). Choose per column and write the reason in the migration.
- `RESTRICT` or `NO ACTION` on a person reference blocks erasure. A test lists such keys and fails.

## Retention jobs

- One resolver answers "how long is this data class kept for this tenant in this state". Jobs ask it; they never
  hard-code days.
- Inputs: data class, plan, account state, legal hold. Recoverable states (suspended, past due, grace period)
  keep the entitled window.
- Run it per tenant, in batches, idempotently. A rerun deletes nothing more than the first run.
- Log counts per class and tenant, never the deleted content.

## Test matrix

| Case | Expected |
|---|---|
| Record one day inside the window, each plan | survives |
| Record one day outside the window, each plan | deleted |
| Suspended or past-due tenant | entitled window, not the free window |
| Invoice of an erased account | kept, non-required personal fields cleared |
| Person erased | zero hits for email and name in a database dump and the storage listing |
| Erasure run twice | second run is a no-op |
