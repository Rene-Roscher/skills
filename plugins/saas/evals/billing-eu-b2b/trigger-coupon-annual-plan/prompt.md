---
description: Should invoke billing-eu-b2b. Run with --ablation none.
expected_outcome: The billing-eu-b2b skill is invoked.
tags: [billing-eu-b2b, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a coupon that takes 10 EUR off the annual plan.
