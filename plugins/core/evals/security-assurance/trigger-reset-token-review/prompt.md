---
description: Should load security-assurance. Train split. Run with --ablation none --threshold 0.5.
tags: [security-assurance, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our password reset tokens are md5 of the email plus the current timestamp. Is that good enough, or what should it be?
