---
description: "Near miss, must not trigger dual-key-identifiers (train split): credential storage. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Hash API keys before storing them.
