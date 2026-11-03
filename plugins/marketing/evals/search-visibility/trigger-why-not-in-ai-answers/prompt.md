---
description: "Should invoke search-visibility. Run with --ablation none."
expected_outcome: "The search-visibility skill is invoked."
tags: [search-visibility, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our booking tool's marketing site barely shows up on Google for "appointment software for physiotherapists", and ChatGPT never mentions us. What should we change on the site?
