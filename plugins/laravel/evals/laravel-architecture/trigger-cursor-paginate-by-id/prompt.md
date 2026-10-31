---
description: Should trigger. Cursor pagination on the internal key. Run with --ablation none.
tags: [laravel-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Is it fine to cursor-paginate the tickets endpoint by id in our Laravel API?
