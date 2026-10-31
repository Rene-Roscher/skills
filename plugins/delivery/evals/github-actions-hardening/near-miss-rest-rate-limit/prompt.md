---
description: "Must not invoke github-actions-hardening (validation split). Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is not invoked."
tags: [github-actions-hardening, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our app hits the GitHub REST API rate limit when syncing issues. Add caching.
