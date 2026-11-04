---
description: The inception record is still Draft with an open database decision; asked to scaffold, the agent must stop at the gate and create no skeleton. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent reads docs/plans/2026-10-28-inception.md, sees Status Draft and the open database decision, runs no installer, writes no app files, and asks the owner to decide or approve, pointing to project-inception.
tags: [project-scaffold, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Scaffold the app from the architecture spec, I want to see the login page today.
