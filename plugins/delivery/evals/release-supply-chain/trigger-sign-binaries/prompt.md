---
description: "Should invoke release-supply-chain. Run with --ablation none."
expected_outcome: "The release-supply-chain skill is invoked."
tags: [release-supply-chain, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Sign the binaries our release workflow attaches to GitHub releases so users can verify them.
