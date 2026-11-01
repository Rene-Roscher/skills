---
type: llm
weight: 3
---

PASS if the migration was changed so the index statements are not inside BEGIN/COMMIT, or the reply states that CREATE INDEX CONCURRENTLY cannot run inside a transaction block and the BEGIN/COMMIT must go or the migration runner transaction wrapper must be off for this file. FAIL if CONCURRENTLY statements stay inside BEGIN...COMMIT without comment.
