---
description: "Must not invoke container-images (train split); github-actions-hardening covers it. Run with --ablation none."
expected_outcome: "The container-images skill is not invoked."
tags: [container-images, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Set least-privilege permissions on our GitHub Actions workflows.
