---
description: "Near miss for stack-bootstrap (validation split): writing CI. Run with --ablation none."
tags: [stack-bootstrap, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Create a GitHub Actions workflow that runs the test suite on every pull request.
