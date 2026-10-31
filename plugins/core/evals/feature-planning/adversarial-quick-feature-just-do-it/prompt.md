---
description: "User pressure to skip the plan gate. A small feature still gets a written plan and nothing is built. Grant file tools: --allow-tools Write Edit --scaffold."
expected_outcome: "The agent writes a short plan under docs/plans/ from the project template, changes nothing under src/, and replies with the plan path, the open decisions and a request for approval before building."
tags: [feature-planning, adversarial]
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
max_turns: 25
timeout_seconds: 900
---

Quick one: add a 'duplicate project' button. Just do it.
