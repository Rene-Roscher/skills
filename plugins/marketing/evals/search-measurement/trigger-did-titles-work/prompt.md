---
description: "Should invoke search-measurement (train split). Run with --ablation none."
expected_outcome: "The search-measurement skill is invoked."
tags: [search-measurement, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Two weeks ago we rewrote the title tags on the twelve venue pages of our booking site. Can you check in Search Console whether that actually brought more clicks?
