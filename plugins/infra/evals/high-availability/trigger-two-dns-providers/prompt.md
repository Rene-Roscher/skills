---
description: Should load high-availability. Validation split. Run with --ablation none --threshold 0.5.
tags: [high-availability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We run all our DNS at one provider. How do we get failover with octoDNS so a provider outage doesn't take every name down?
