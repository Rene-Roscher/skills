---
description: Should load async-reliability. Validation split. Run with --ablation none --threshold 0.5.
tags: [async-reliability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We run three app replicas. Add a nightly scheduled task that expires unpaid reservations.
