---
description: "Near miss for performance-gate (train split): page-load speed. Run with --ablation none."
tags: [performance-gate, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The landing page scores badly in Lighthouse. Make the hero image load faster.
