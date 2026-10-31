---
description: Must not trigger; belongs to tenant-isolation. Run with --ablation none.
tags: [laravel-architecture, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Can tenant A see tenant B's tickets through the CSV export? How do we check?
