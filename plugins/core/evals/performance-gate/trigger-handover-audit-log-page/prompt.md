---
description: "Should trigger performance-gate (train split). Run with --ablation none."
tags: [performance-gate, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The new audit log page is finished. Before I hand it over, check that it holds up for our largest tenants.
