---
description: "Should invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is invoked."
tags: [cross-service-contracts, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

How do we make sure our Node consumer and our Go producer keep agreeing on the event format when they live in different repos?
