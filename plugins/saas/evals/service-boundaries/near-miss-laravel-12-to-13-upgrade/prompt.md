---
description: "Near miss: must not trigger service-boundaries (validation split). Run with --ablation none."
expected_outcome: "The service-boundaries skill is not invoked."
tags: [service-boundaries, near-miss]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Upgrade from Laravel 12 to 13.
