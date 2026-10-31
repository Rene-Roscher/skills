---
description: Should trigger. Wake-up jobs delayed behind bulk work. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

In our Laravel payments app, the fraud alerts to the analyst on duty arrive minutes late whenever the weekly newsletter goes out.
