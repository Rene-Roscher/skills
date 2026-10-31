---
description: "Near miss, must not trigger authorization-rbac (train split): dual-key-identifiers. Run with --ablation none."
tags: [authorization-rbac, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Use NanoID instead of numeric IDs in URLs.
