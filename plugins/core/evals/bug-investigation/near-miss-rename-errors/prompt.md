---
description: "Near miss, must not trigger bug-investigation (validation split): refactoring. Run with --ablation none."
tags: [bug-investigation, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename the error classes to end in Exception.
