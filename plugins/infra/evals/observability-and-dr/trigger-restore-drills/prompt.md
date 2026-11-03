---
description: Should load observability-and-dr. Validation split. Run with --ablation none --threshold 0.5.
tags: [observability-and-dr, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We run nightly database backups but have never restored one. How should we set up restore drills?
