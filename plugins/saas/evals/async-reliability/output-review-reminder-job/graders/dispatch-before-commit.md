---
type: llm
weight: 3
---

PASS if the reply flags that the job is dispatched inside the transaction without afterCommit (or an outbox), so it can run before the booking is committed or after a rollback. FAIL if not mentioned.
