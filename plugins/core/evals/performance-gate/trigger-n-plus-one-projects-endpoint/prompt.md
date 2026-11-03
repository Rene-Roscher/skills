---
description: "Should trigger performance-gate (train split). Run with --ablation none."
tags: [performance-gate, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Will GET /api/projects run one query per project once a tenant has 5,000 projects? Measure it.
