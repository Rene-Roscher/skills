---
type: llm
weight: 3
---

PASS if the reply explains that the ALTER TABLE lock is held until the transaction ends, so DDL and a long UPDATE in one transaction block the table, or that one huge UPDATE creates dead rows and long locks. FAIL if it gives no reason for splitting.
