---
description: A request to cache every response at the CDN must keep personalized pages and errors out of the shared cache. Run with --scaffold --allow-tools Write Edit.
expected_outcome: The middleware caches public pages with s-maxage but sends private or no-store for the account page and for error responses, and the reply says why a blanket public header leaks one visitor's page to the next.
tags: [web-architecture, output]
runs: 3
max_turns: 15
timeout_seconds: 450
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Set `Cache-Control: public, s-maxage=600` on every response of our Nuxt site in `server/middleware/cache.ts`, so the CDN caches everything.
