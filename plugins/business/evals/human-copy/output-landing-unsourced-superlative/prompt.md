---
description: An English landing draft with an unsourced superlative, an invented customer count and tell phrases must come back sourced, concrete and without them. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent rewrites copy/landing.md from copy/facts.md: the superlative and the customer count are gone or marked as needing a source, the 30-second interval and four locations appear, and the tell phrases and the generic button are gone.
tags: [human-copy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Rewrite copy/landing.md in place so it reads like a person wrote it for a reader who runs a small agency. Use only what copy/facts.md confirms. Tell me what you could not back up.
