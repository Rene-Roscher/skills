---
description: "Should invoke release-supply-chain. Run with --ablation none."
expected_outcome: "The release-supply-chain skill is invoked."
tags: [release-supply-chain, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a release notes template for our CLI that tells users how to check the downloads are genuine.
