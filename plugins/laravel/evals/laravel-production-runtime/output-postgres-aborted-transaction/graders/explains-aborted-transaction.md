---
type: llm
weight: 1
---

PASS if the reply explains that after an error inside a transaction PostgreSQL rejects every further statement until a rollback or a rollback to a savepoint, so catching the duplicate-key exception and continuing cannot work there, while SQLite carries on.
FAIL if the reply calls the failure flaky, blames test isolation alone, or keeps catching the exception and querying in the same transaction.
