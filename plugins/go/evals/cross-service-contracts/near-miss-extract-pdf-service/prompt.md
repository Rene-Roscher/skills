---
description: "Must not invoke cross-service-contracts. Run with --ablation none."
expected_outcome: "The cross-service-contracts skill is not invoked."
tags: [cross-service-contracts, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Should we move PDF rendering out of our Laravel monolith into a separate Go service?
