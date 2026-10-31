---
description: Should trigger. Datetime offsets dropped before the write. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Times saved through our Laravel API are an hour off for some clients.
