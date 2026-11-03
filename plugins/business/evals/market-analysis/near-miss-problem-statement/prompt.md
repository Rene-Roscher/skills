---
description: "Must not invoke market-analysis; this belongs to product-strategy (train split). Run with --ablation none."
expected_outcome: "The market-analysis skill is not invoked."
tags: [market-analysis, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write the problem statement and the buyer and user personas for our booking product brief.
