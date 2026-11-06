---
description: Should load security-assurance. Validation split. Run with --ablation none --threshold 0.5.
tags: [security-assurance, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We store customers' third-party API keys in the database. How should we encrypt them, and how do we know it actually holds up?
