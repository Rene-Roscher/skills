---
description: "Near miss, must not trigger dual-key-identifiers (train split): plain schema change. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename `customer_name` to `name` in the migration.
