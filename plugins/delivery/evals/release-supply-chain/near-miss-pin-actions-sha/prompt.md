---
description: "Must not invoke release-supply-chain. Run with --ablation none."
expected_outcome: "The release-supply-chain skill is not invoked."
tags: [release-supply-chain, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Pin all actions in our workflows to commit SHAs.
