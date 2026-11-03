---
type: llm
weight: 2
---

PASS if the reply says the liveness probe must not depend on the database (or any shared dependency) and proposes a separate liveness endpoint, keeping the database check, if any, in readiness. FAIL if liveness still checks the database or both probes keep the same endpoint without comment.
