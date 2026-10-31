---
description: "Near miss, must not trigger authorization-rbac (validation split): CI hardening. Run with --ablation none."
tags: [authorization-rbac, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Configure GitHub Actions `permissions:` for the release job.
