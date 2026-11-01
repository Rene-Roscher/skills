---
type: llm
weight: 2
---

PASS if any PodDisruptionBudget the reply proposes allows at least one eviction at a time (for example maxUnavailable 1 or minAvailable below the replica count) together with at least two replicas, or the reply warns that maxUnavailable 0 would block node drains. FAIL if it proposes a budget with maxUnavailable 0 or minAvailable equal to the replica count without that warning, or proposes a budget while leaving one replica.
