---
description: Should trigger. Splitting a very large Laravel controller. Run with --ablation none.
tags: [laravel-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this Laravel controller, it's about 2,000 lines. How do we split it without breaking the routes?
