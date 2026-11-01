---
type: llm
weight: 3
---

PASS if the reply says a plain CREATE INDEX blocks writes (inserts, updates, deletes) on the table while it builds, and that CREATE INDEX CONCURRENTLY avoids this. FAIL if it only reformats the file or says the migration is fine.
