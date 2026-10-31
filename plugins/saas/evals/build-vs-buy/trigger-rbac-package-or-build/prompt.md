---
description: Should invoke build-vs-buy. Run with --ablation none.
expected_outcome: The build-vs-buy skill is invoked.
tags: [build-vs-buy, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Should we use a package for roles and permissions in our project tool, or build it ourselves?
