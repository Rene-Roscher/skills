---
type: llm
weight: 3
---

PASS if the reply says that the report's claim that `projects` already has an `archived_at` column is contradicted by db/schema.sql, and the plan includes adding that column (a migration or schema change).
FAIL if the plan says no migration is needed, or repeats the report's claim about `archived_at` as fact.
