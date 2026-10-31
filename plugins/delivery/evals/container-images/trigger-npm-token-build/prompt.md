---
description: "Should invoke container-images (train split). Run with --ablation none."
expected_outcome: "The container-images skill is invoked."
tags: [container-images, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The docker build needs an npm token for a private registry. How do I pass it in?
