---
description: Should invoke billing-eu-b2b. Run with --ablation none.
expected_outcome: The billing-eu-b2b skill is invoked.
tags: [billing-eu-b2b, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Our payment webhook sometimes returns 500 when two calls for the same payment arrive together. Fix it.
