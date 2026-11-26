---
description: Should load audience-gate. Validation split. Run with --ablation none --threshold 0.5.
tags: [audience-gate, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a CI step that stops the deploy when the built site contains placeholders, TODOs or notes meant for the team.
