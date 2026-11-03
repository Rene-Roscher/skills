---
description: "Must not invoke market-analysis; this belongs to pricing-and-unit-economics (train split). Run with --ablation none."
expected_outcome: "The market-analysis skill is not invoked."
tags: [market-analysis, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Team plan costs us 3.10 EUR per customer per month in SMS and 1.20 EUR in hosting. What margin do we make at 29 EUR net?
