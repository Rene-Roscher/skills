---
description: On a repository with code and no docs the agent writes an as-built spec from the code with path and line evidence, records drift, changes no code and stops at the gate. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: "The agent writes docs and AGENTS.md only: a spec whose statements cite path:line, a Code: header and check date, an inception record in Draft with a drift table, and runs the docs checker. The README claim about the cancellation window is listed as drift, not silently fixed."
tags: [project-inception, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

This repo has no docs. Set up docs/ so agents can work on it. Describe what the code does today.
