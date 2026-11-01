---
description: Should load test-strategy. Run with --ablation none --threshold 0.5.
tags: [test-strategy, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our manager wants 90% line coverage across the whole repository before the next release. How should we set the coverage gate in CI?
