---
type: llm
weight: 3
---

PASS if the reply recommends building the pricing page outside the Laravel + Inertia product app, as a separate public site with its own deployment, and gives at least one of these reasons: the page stays up when the product runtime is down or frozen (failure domain), prerendering and CDN caching, or URLs and headers that stay stable across product releases (SEO stability). If the reply offers to build the page inside the app anyway, it must say that this deviates from the default and needs an ADR naming the trade-off.
FAIL if the reply adds the page as an app route without that caveat, or argues mainly with PHP or framework speed.
