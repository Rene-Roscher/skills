---
description: "Should trigger interface-motion (validation). Run with --ablation none."
tags: [interface-motion, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make the slide-over respect reduced motion without breaking how it opens and closes.
