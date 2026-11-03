---
description: "Should invoke go-service-baseline. Run with --ablation none."
expected_outcome: "The go-service-baseline skill is invoked."
tags: [go-service-baseline, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Set up a new Go worker that pulls jobs from a queue and exposes Prometheus metrics. What should main.go and the package layout look like?
