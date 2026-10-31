---
description: Should trigger. Editing the Octane flush list. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add our TenantContext service to octane.flush so it resets between requests.
