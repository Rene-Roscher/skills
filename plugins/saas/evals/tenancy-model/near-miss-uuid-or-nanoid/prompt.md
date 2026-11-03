---
description: "Near miss, must not trigger tenancy-model (train split): dual-key-identifiers. Run with --ablation none."
tags: [tenancy-model, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Should our organization IDs in URLs be UUIDv7 or NanoID?
