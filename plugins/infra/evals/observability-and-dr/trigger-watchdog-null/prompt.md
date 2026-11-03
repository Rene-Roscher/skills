---
description: Should load observability-and-dr. Train split. Run with --ablation none --threshold 0.5.
tags: [observability-and-dr, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Alertmanager routes the Watchdog alert to a null receiver. Is that a problem, and what should we do instead?
