---
description: "Near miss, must not trigger tenant-isolation (train split): dual-key-identifiers. Run with --ablation none."
tags: [tenant-isolation, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Should IDs be UUIDv7 or NanoID?
