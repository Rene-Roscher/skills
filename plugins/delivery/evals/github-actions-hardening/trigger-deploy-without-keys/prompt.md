---
description: "Should invoke github-actions-hardening (train split). Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is invoked."
tags: [github-actions-hardening, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We want to deploy to AWS from GitHub Actions without storing access keys in secrets.
