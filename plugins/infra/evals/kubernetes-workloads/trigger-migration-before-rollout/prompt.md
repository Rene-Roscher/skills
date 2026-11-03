---
description: Should load kubernetes-workloads. Validation split. Run with --ablation none --threshold 0.5.
tags: [kubernetes-workloads, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

How do we make sure the database migration Job finishes before the new app pods start rolling out when we deploy with Flux?
