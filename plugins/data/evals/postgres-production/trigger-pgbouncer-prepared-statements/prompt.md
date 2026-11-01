---
description: Should load postgres-production. Validation split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We moved to PgBouncer in transaction mode and now some requests fail with prepared statement errors and our SET statement_timeout seems random. What should we change?
