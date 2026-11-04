---
description: Must not load glossary; a general coding question with no ecosystem term. Run with --ablation none --threshold 0.5.
tags: [glossary, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Why does this Python snippet return an empty list? `[x for x in range(10) if x > 10]`
