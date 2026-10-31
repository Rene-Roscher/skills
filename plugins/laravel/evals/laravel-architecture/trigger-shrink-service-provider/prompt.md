---
description: Should trigger. Splitting an overloaded service provider. Run with --ablation none.
tags: [laravel-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make our Laravel AppServiceProvider smaller. It has rate limiters, container bindings and event listeners in one file.
