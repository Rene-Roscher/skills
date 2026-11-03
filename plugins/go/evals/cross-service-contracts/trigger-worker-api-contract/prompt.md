---
description: "Should invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is invoked."
tags: [cross-service-contracts, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write down the API between our Laravel control plane and the Go probe workers: registration, config pull and heartbeats.
