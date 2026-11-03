---
description: Should load async-reliability. Train split. Run with --ablation none --threshold 0.5.
tags: [async-reliability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our invoice mail job sometimes runs twice and customers get two copies. How do we stop that?
