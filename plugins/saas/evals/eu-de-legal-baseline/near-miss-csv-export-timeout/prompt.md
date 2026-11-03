---
description: "Near miss: must not trigger eu-de-legal-baseline (validation split). Run with --ablation none."
expected_outcome: "The eu-de-legal-baseline skill is not invoked."
tags: [eu-de-legal-baseline, near-miss]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The CSV export of 200,000 time entries times out after 30 seconds. Make it stream instead of building the file in memory.
