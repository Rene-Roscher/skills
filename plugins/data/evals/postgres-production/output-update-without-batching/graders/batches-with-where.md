---
type: llm
weight: 3
---

PASS if the reply or the resulting files backfill in batches (a key range or LIMIT per batch, each with a WHERE clause) with a commit per batch, run as a step separate from the ALTER TABLE. FAIL if a single UPDATE over all rows remains, or the backfill still shares one transaction with the DDL.
