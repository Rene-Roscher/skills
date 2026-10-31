---
description: Should invoke build-vs-buy. Run with --ablation none.
expected_outcome: The build-vs-buy skill is invoked.
tags: [build-vs-buy, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Set up mail failover: primary provider, secondary provider, then log.
