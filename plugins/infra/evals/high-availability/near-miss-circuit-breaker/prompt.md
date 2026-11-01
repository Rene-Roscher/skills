---
description: Must not load high-availability. Validation split. Run with --ablation none --threshold 0.5.
tags: [high-availability, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a retry with exponential backoff and a circuit breaker around the call to the payment API in my Node service.
