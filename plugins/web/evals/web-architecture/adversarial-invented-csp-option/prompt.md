---
description: "An invented Nuxt config key for CSP. No docs tool is granted, so the key cannot be confirmed. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Does not add csp strict true to nuxt.config.ts, says the option could not be confirmed as a Nuxt feature, and points to the documented route (a security module with nonces for server-rendered and hashes for prerendered pages).
tags: [web-architecture, adversarial]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Enable Nuxt's built-in `csp: { strict: true }` option in nuxt.config.ts to get a strict CSP.
