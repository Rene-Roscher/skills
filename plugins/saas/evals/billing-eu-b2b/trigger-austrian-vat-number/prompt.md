---
description: Should invoke billing-eu-b2b. Run with --ablation none.
expected_outcome: The billing-eu-b2b skill is invoked.
tags: [billing-eu-b2b, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

A customer in Austria entered a VAT number. What do we charge on the next renewal?
