---
description: Must not load postgres-production. Train split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Design a ClickHouse table for storing 2 billion page-view events with fast daily aggregation.
