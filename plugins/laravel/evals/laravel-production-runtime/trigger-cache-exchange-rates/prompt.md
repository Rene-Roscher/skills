---
description: Should trigger. Validated caching of a third-party response. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

In our Laravel app, cache the exchange rates from the external API, but not when it returns an error.
