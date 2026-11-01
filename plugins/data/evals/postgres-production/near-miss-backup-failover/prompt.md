---
description: Must not load postgres-production. Validation split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Set up PostgreSQL streaming replication with automatic failover and nightly offsite backups with point-in-time recovery.
