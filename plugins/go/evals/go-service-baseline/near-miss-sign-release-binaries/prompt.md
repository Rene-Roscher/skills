---
description: "Must not invoke go-service-baseline. Run with --ablation none."
expected_outcome: "The go-service-baseline skill is not invoked."
tags: [go-service-baseline, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Change our GitHub release workflow so the attached binaries are signed with cosign and users can verify them.
