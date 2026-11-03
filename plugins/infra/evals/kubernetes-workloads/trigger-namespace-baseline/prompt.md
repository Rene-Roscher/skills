---
description: Should load kubernetes-workloads. Train split. Run with --ablation none --threshold 0.5.
tags: [kubernetes-workloads, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our application namespaces have no Pod Security labels, no quotas and no NetworkPolicies. What should a baseline for each namespace look like?
