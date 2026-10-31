---
description: "Should invoke container-images (validation split). Run with --ablation none."
expected_outcome: "The container-images skill is invoked."
tags: [container-images, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Trivy shows 120 HIGH findings in our image. What do we do?
