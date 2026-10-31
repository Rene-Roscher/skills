---
description: Should trigger. Arch tests that fence the Validator facade. Run with --ablation none.
tags: [laravel-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write Pest arch tests that make sure our Laravel controllers never touch the Validator facade.
