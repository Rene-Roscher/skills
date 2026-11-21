---
description: "Should trigger interface-motion (train). Run with --ablation none."
tags: [interface-motion, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Give the sidebar collapse a spring, but we don't want to add an animation library.
