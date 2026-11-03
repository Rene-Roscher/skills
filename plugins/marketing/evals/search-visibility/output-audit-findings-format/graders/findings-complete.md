---
type: llm
weight: 4
---

PASS if the reply reports all four issues: (1) the English features page canonicalises to the home page instead of itself, (2) the hreflang annotation is one-way because the German page does not link back (and lacks a self-reference), (3) the pricing page's content is not in the server HTML (empty app container rendered by JavaScript), (4) old-pricing.html uses a meta refresh instead of a 301 or 308 redirect. Each finding states a severity, the URL or file, the evidence, the fix and how to verify the fix.
FAIL if any of the four is missing, if findings lack evidence or a verification step, if the reply recommends noindex on one language version, or if it states ranking positions or traffic figures it did not measure.
