---
description: "Must not invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is not invoked."
tags: [cross-service-contracts, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename a column in our PostgreSQL table without downtime.
