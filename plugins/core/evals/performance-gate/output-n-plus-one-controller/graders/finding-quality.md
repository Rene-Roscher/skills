---
type: llm
weight: 3
---

PASS if the reply (1) identifies both per-row queries, the owner relation and the open-task count, (2) states the magnitude as a function of the number of projects (about 2N + 1 queries) and puts in a concrete large N, (3) proposes eager loading the owner and a conditional withCount (or an equivalent single aggregate query), (4) flags loading every project without pagination or a limit, and (5) asks for a query-budget test that gives the same count for 1 and many projects, with a frozen clock.
FAIL if any of the five is missing, or if it claims measured numbers it could not have measured without saying they are estimates.
