---
type: llm
weight: 3
---

PASS if the plan is memoized without process-wide state: a `scoped()` binding with instance state, a token on the current request, or a cache entry tagged by tenant with invalidation when the plan changes. The reply must say that a static array survives into later requests and jobs on the same Octane or queue worker, so a plan change stays invisible and memory grows, and it must report that `octane_scan.py` ran (naming its tokenizer mode) and exited 0, or give the exact command if it could not run.
FAIL if PlanResolver keeps the plan in a static property, a function-level static or a singleton, or if the reply calls a static cache safe because it is keyed by tenant id.
