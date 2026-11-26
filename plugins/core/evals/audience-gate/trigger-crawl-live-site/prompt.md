---
description: Should load audience-gate. Train split. Run with --ablation none --threshold 0.5.
tags: [audience-gate, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Go through every page of https://example.com and tell me if any of them shows internal notes, placeholders or half-finished text.
