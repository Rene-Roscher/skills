---
description: Should trigger. Device management on cache-backed sessions. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Users want to see and log out their other devices. Our Laravel sessions are in Redis.
