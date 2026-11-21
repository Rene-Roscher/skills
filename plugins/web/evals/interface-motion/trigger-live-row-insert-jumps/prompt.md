---
description: "Should trigger interface-motion (validation). Run with --ablation none."
tags: [interface-motion, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

When a new booking row arrives live, the table rows jump. Animate the insert smoothly.
