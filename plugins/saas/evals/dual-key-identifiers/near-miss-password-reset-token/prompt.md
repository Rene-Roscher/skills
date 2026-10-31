---
description: "Near miss, must not trigger dual-key-identifiers (train split): a secret, not a record ID. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Generate a password reset token.
