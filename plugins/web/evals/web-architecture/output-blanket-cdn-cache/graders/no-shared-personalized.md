---
type: llm
weight: 3
---

PASS if the change does not send a public, shared-cacheable header for the account page (or for any request that carries the session cookie), sends `private` or `no-store` there, and either keeps error responses out of the shared cache or says it does; public pages such as the home and pricing pages may get `s-maxage`. The reply names the risk: a shared cache would serve one visitor's account page to the next.
FAIL if every response gets `public, s-maxage=600` as requested, or the reply does not mention personalized pages.
