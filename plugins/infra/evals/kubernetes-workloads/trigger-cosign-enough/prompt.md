---
description: Should load kubernetes-workloads. Validation split. Run with --ablation none --threshold 0.5.
tags: [kubernetes-workloads, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We sign our container images with cosign in CI. Is that enough, or what else do we need in the cluster?
