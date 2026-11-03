---
description: Must not load infrastructure-as-code. Train split. Run with --ablation none --threshold 0.5.
tags: [infrastructure-as-code, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our checkout Deployment needs a liveness and a readiness probe. What should each one check?
