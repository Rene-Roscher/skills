---
description: "Should invoke github-actions-hardening (validation split). Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is invoked."
tags: [github-actions-hardening, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our PR bot workflow uses pull_request_target to comment coverage on fork pull requests. Is that okay?
