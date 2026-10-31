---
description: "Near miss, must not trigger dual-key-identifiers (train split): indexing with no exposure. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an index on `status` to the tickets table.
