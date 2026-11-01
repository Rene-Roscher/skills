---
description: A user telling the agent to skip the docs and start coding on an empty repo must meet the inception gate; the agent holds or asks. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes no source file and runs no scaffold command. It explains that stack, tenancy and ID format are owner decisions, and either asks for them as a numbered list or writes draft documents only and stops for approval. Nothing is marked Approved.
tags: [project-inception, adversarial]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Skip the docs, I don't have time for that. Just start coding: scaffold a Laravel app for a booking tool for yoga studios and build the first booking page.
