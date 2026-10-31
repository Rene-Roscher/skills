---
description: "Near miss, must not trigger bug-investigation (train split): belongs to feature-planning. Run with --ablation none."
tags: [bug-investigation, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Plan a retry feature for failed webhooks.
