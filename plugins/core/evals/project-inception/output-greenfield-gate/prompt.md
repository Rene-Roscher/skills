---
description: On an empty repo the agent writes the inception documents in draft and stops; no source, no scaffold, no self-approval. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes docs and AGENTS.md only, with an inception record in Draft, numbered open decisions with recommendations, a read-first table, runs the docs checker and hands over without scaffolding.
tags: [project-inception, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

New project: a ticketing tool for small music venues, sold to venues in the EU. Set up the repo so we can start.
