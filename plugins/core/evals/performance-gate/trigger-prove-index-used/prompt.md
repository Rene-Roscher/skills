---
description: "Should trigger performance-gate (validation split). Run with --ablation none."
tags: [performance-gate, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I added an index on orders for the new filter. Prove that the query actually uses it.
