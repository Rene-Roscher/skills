---
description: "Should invoke market-analysis (train split). Run with --ablation none."
expected_outcome: "The market-analysis skill is invoked."
tags: [market-analysis, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our market analysis is from spring. Refresh it before we decide on the new plans for the booking system.
