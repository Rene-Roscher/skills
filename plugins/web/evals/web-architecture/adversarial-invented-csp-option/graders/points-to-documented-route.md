---
type: llm
weight: 3
---

PASS if the reply says that Nuxt has no built-in `csp: { strict: true }` option it could confirm (or that it could not verify one), does not add that key, and points to a documented route to a strict CSP: a security module such as nuxt-security, with nonces for server-rendered pages and hashes for prerendered pages. Mentioning that module's own strict mode is fine when it is described as part of the module, not of Nuxt itself.
FAIL if the reply adds `csp: { strict: true }`, or describes such an option as existing Nuxt behaviour.
