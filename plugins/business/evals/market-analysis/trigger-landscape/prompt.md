---
description: "Should invoke market-analysis (validation split). Run with --ablation none."
expected_outcome: "The market-analysis skill is invoked."
tags: [market-analysis, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Map the competitive landscape for our project tool for small architecture offices: the 20 most relevant vendors, how they package and price, and where the gaps are.
