---
description: "Must not invoke github-actions-hardening (train split); container-images covers it. Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is not invoked."
tags: [github-actions-hardening, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make this Dockerfile smaller and run it as non-root.
