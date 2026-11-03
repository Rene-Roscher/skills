---
description: "Harden a dev compose file that uses default host ports, no project name, restart always and no health gating. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "compose.yaml gets a fixed name, host ports from a non-default block bound to 127.0.0.1, healthchecks with service_healthy, no restart always; a Makefile with up and doctor targets; an .env.example with the port values."
tags: [local-dev-stack, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

I run several projects on this workstation and this one keeps clashing with the others. Make its local stack safe to run next to them and give me one command to start it.
