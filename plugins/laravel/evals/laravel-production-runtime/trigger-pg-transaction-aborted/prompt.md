---
description: Should trigger. A failure that appears only on PostgreSQL. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Laravel tests are green locally but red in CI on Postgres, something about 'current transaction is aborted'.
