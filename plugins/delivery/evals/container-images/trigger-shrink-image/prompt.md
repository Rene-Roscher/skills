---
description: "Should invoke container-images (train split). Run with --ablation none."
expected_outcome: "The container-images skill is invoked."
tags: [container-images, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our container image is 1.4 GB. Can you make it smaller?
