---
description: Must not load kubernetes-workloads. Validation split. Run with --ablation none --threshold 0.5.
tags: [kubernetes-workloads, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Go service leaks goroutines under load. How do I find the leak with pprof?
