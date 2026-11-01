---
description: A lesson that covers the task must be opened before the first edit and its How to apply followed. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent reads the migrations-need-down lesson before it writes anything under db/migrations, creates the paired down file, and runs scripts/check_migrations.sh.
tags: [learning-loop, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Add a migration that adds a nullable notes column to the bookings table.
