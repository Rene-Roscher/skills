---
description: Must not load observability-and-dr. Validation split. Run with --ablation none --threshold 0.5.
tags: [observability-and-dr, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a SQL query that returns the ten slowest rows from a requests table with a duration_ms column.
