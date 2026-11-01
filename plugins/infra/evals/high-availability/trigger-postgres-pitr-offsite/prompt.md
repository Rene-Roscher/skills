---
description: Should load high-availability. Validation split. Run with --ablation none --threshold 0.5.
tags: [high-availability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Design backups for our CloudNativePG cluster: WAL archiving, point in time recovery and an off-site copy. What RPO and RTO can we promise?
