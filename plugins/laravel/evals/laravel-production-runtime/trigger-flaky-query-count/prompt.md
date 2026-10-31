---
description: Should trigger. Query-count tests that flake. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make the query-count test in our Laravel suite stop being flaky in CI.
