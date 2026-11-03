---
description: Should load agent-delegation. Validation split. Run with --ablation none --threshold 0.5.
tags: [agent-delegation, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Spin up a bunch of parallel agents to go through the project tool's backend and look for anything suspicious. As many as you like.
