---
description: "Near miss for stack-bootstrap (train split): an application dependency. Run with --ablation none."
tags: [stack-bootstrap, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add laravel/horizon to composer.json and publish its config.
