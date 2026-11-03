---
description: "Must not invoke market-analysis; this belongs to human-copy (validation split). Run with --ablation none."
expected_outcome: "The market-analysis skill is not invoked."
tags: [market-analysis, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rewrite the headline on our pricing page so it sounds less like marketing.
