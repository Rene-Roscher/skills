---
description: "Must not invoke container-images (validation split). Run with --ablation none."
expected_outcome: "The container-images skill is not invoked."
tags: [container-images, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a systemd unit for this binary.
