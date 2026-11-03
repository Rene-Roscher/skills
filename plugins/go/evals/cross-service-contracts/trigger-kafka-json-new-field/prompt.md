---
description: "Should invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is invoked."
tags: [cross-service-contracts, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Go producer writes check results as JSON to Kafka, and a Rust service and a Laravel app consume them. Add a `region` field to the event.
