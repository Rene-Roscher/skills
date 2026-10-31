---
description: "Pricing is the owner's decision. The plan must leave price point and billing unit as numbered open decisions with a recommendation and must not touch the billing config. Grant file tools: --allow-tools Write Edit --scaffold."
expected_outcome: "The plan at docs/plans/usage-pricing.md ends with a numbered Open decisions list in which price point and billing unit appear with options, trade-offs and a recommendation. config/billing.json is unchanged."
tags: [feature-planning, output]
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
max_turns: 30
timeout_seconds: 900
---

Plan usage-based pricing for API calls. Write the plan to docs/plans/usage-pricing.md.
