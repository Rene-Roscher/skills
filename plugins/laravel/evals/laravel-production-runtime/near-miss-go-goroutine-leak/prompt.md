---
description: Must not trigger; not Laravel. Run with --ablation none.
tags: [laravel-production-runtime, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Go worker leaks goroutines. How do we find where?
