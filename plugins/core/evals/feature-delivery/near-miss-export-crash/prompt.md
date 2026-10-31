---
description: "Near miss, must not trigger feature-delivery (train split): belongs to bug-investigation. Run with --ablation none."
tags: [feature-delivery, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Why does the export crash on empty lists?
