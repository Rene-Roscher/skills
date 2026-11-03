---
description: "Move a project with children to another organization. Needs --scaffold."
expected_outcome: "The reply checks the target organization's project limit through ProjectLimits before changing rows, rewrites organization_id on the project, tasks and comments in one transaction, and handles project members who are not members of the target organization."
tags: [tenancy-model, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a MoveProjectToOrganization service that moves a project with its tasks and comments into another organization the acting user belongs to. Reply with code and tests; do not write files.
