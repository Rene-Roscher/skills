---
description: Must not trigger; query and index design. Run with --ablation none.
tags: [laravel-production-runtime, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Design a Postgres index for this slow query: SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 50.
