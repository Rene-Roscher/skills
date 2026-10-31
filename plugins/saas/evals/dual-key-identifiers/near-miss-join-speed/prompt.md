---
description: "Near miss, must not trigger dual-key-identifiers (train split): join performance with no external exposure. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Speed up the join between `orders` and `order_items`.
