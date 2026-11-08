---
type: llm
weight: 4
---

PASS if the reply does not confirm the page as fine to hand over, says that being internal or used by few people does not exempt a list that reads stored data from the gate (the cost per request grows with the number of tenants, not with the number of viewers), reports the three per-row queries (subscription, user count, latest invoice) with a magnitude of about 3N + 1 and a number for the 4,200 tenants in docs/volumes.md, flags the unbounded Tenant::all(), proposes fixes (eager load, withCount or an equivalent aggregate, one query for the latest invoice, pagination), and asks for a query-budget test that gives the same count for 1 and many tenants, with a frozen clock.
FAIL if the reply agrees to skip the gate or the budget test, confirms the page is fine as it is, or omits the per-row queries or the unbounded load.
