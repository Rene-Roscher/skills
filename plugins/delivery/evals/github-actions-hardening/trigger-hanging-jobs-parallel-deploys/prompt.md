---
description: "Should invoke github-actions-hardening (validation split). Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is invoked."
tags: [github-actions-hardening, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our CI jobs sometimes hang for hours, and two deploy workflow runs went out at the same time yesterday.
