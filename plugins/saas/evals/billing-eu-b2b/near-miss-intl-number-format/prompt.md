---
description: Near miss for billing-eu-b2b; the skill must not be invoked. Run with --ablation none.
expected_outcome: The billing-eu-b2b skill is not invoked.
tags: [billing-eu-b2b, near-miss]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Format 1234.5 as a euro amount in Vue with Intl.NumberFormat.
