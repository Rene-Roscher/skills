---
description: "Must not invoke search-measurement; this belongs to search-visibility (train split). Run with --ablation none."
expected_outcome: "The search-measurement skill is not invoked."
tags: [search-measurement, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Every venue page on our booking site has a canonical tag pointing to the home page. Which canonical should each venue page declare, and what about the paginated venue list?
