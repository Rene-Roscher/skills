---
description: "Near miss for interface-motion (train): layering belongs to design-quality. Run with --ablation none."
tags: [interface-motion, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The confirm dialog renders behind the slideover. Fix the stacking order.
