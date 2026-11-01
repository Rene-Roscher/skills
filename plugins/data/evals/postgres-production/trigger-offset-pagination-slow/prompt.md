---
description: Should load postgres-production. Validation split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Page 4000 of our invoice list in PostgreSQL takes seconds and sometimes shows the same invoice twice. How should we paginate?
