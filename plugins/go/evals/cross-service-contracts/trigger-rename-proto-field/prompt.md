---
description: "Should invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is invoked."
tags: [cross-service-contracts, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename the `latency` field in our worker.proto to `latency_ms`. The Go worker and the PHP control plane both use this message.
