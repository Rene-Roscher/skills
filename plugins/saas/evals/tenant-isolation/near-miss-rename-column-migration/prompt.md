---
description: "Near miss, must not trigger tenant-isolation (validation split): plain schema change. Run with --ablation none."
tags: [tenant-isolation, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a migration that renames a column.
