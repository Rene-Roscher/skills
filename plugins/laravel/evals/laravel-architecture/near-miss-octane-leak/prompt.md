---
description: Must not trigger; belongs to laravel-production-runtime. Run with --ablation none.
tags: [laravel-architecture, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Why does our Laravel Octane worker sometimes show the previous user's data?
