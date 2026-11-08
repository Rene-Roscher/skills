---
description: Must not load executor-spec; a search subagent inside the session is agent-delegation territory. Validation split. Run with --ablation none --threshold 0.5.
tags: [executor-spec, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Spawn a quick subagent to find every caller of parseDate in this repository and give me the list.
