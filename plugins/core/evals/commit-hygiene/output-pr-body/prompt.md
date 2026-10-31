---
description: A PR description for a one-line change stays short, has a Tested line and no template headings, credit line or emoji. Needs --scaffold and --allow-tools Bash Write.
expected_outcome: The agent writes a description of under 80 words: what changes for whom, why, a Tested line with what it ran, no headings, no checklist, no credit line.
tags: [commit-hygiene, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Write the pull request description for this branch into PR_BODY.md. Do not open the pull request.
