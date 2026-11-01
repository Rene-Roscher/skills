---
description: Should load maintainable-code. Run with --ablation none --threshold 0.5.
tags: [maintainable-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Two of our request handlers look almost identical. Should I extract a shared function, or leave them?
