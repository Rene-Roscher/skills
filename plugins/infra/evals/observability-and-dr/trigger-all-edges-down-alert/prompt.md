---
description: Should load observability-and-dr. Train split. Run with --ablation none --threshold 0.5.
tags: [observability-and-dr, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Prometheus alert rule that fires when every instance of our edge job is down.
