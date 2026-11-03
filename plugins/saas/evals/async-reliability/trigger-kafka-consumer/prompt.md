---
description: Should load async-reliability. Validation split. Run with --ablation none --threshold 0.5.
tags: [async-reliability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a Kafka consumer that writes incoming check results into the reports table.
