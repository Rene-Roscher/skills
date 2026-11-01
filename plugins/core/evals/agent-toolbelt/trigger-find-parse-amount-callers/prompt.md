---
description: Should load agent-toolbelt. Run with --ablation none --threshold 0.5.
tags: [agent-toolbelt, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Find every place in this repository that calls parse_amount and tell me which callers pass a string literal.
