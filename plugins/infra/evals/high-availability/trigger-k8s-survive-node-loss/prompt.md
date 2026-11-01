---
description: Should load high-availability. Validation split. Run with --ablation none --threshold 0.5.
tags: [high-availability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Kubernetes deployments keep going down when a node is drained for upgrades. What do we need so the booking app stays up?
