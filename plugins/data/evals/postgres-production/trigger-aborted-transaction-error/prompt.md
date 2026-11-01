---
description: Should load postgres-production. Train split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

In production we get 'current transaction is aborted, commands ignored until end of transaction block' after we catch a duplicate email error in our signup code. Tests on SQLite never show it. What is going on?
