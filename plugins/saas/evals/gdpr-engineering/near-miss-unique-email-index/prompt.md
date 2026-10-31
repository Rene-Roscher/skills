---
description: "Near miss: must not trigger gdpr-engineering (train split). Run with --ablation none."
expected_outcome: "The gdpr-engineering skill is not invoked."
tags: [gdpr-engineering, near-miss]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a unique index on users.email.
