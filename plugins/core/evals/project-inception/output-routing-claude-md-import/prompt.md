---
description: AGENTS.md holds the routing table and a CLAUDE.md exists without the import; the agent must find why the table is ignored and add the import. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent explains that Claude Code reads AGENTS.md only when no CLAUDE.md exists, adds @AGENTS.md on its own line at the top of CLAUDE.md, keeps the table in AGENTS.md and runs the docs checker clean.
tags: [project-inception, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Claude does not seem to follow the read-first table in AGENTS.md. Find out why and fix it.
