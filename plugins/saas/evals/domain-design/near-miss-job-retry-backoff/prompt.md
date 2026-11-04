---
description: "Near miss: must not trigger domain-design (train split). Run with --ablation none."
expected_outcome: "The domain-design skill is not invoked."
tags: [domain-design, near-miss]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our invoice PDF job fails when the storage API times out. Add retries with exponential backoff and a dead-letter queue.
