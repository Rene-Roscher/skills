---
description: "Should trigger bug-investigation (train split). Run with --ablation none."
tags: [bug-investigation, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Users report that totals are off by one cent for some carts.
