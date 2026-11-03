---
description: "Should invoke market-analysis (train split). Run with --ablation none."
expected_outcome: "The market-analysis skill is invoked."
tags: [market-analysis, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

What do the main invoicing apps for freelancers charge, and where should our Pro plan sit against them?
