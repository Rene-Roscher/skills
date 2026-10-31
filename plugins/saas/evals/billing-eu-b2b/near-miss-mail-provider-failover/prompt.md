---
description: Near miss for billing-eu-b2b; the skill must not be invoked. Run with --ablation none.
expected_outcome: The billing-eu-b2b skill is not invoked.
tags: [billing-eu-b2b, near-miss]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Switch our transactional email provider and add failover.
