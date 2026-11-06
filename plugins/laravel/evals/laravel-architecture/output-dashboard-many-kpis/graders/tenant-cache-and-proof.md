---
type: llm
weight: 3
---

PASS if the reply (1) says each expensive widget loads separately (deferred groups or when visible) instead of in one request, (2) caches widget results with a key that includes the tenant (and the viewer's visibility where data differs per viewer) and a TTL chosen per widget, and (3) names how it proves the result: a test that the first response lacks the deferred props, or cold and warm query counts per widget.
FAIL if all KPIs are still computed in the first request, if a cache key has no tenant, or if no proof is named.
