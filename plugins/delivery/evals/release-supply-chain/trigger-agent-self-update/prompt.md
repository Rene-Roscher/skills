---
description: "Should invoke release-supply-chain. Run with --ablation none."
expected_outcome: "The release-supply-chain skill is invoked."
tags: [release-supply-chain, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our agent updates itself by downloading the newest binary from our CDN. Make that safe.
