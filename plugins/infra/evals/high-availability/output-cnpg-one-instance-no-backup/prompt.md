---
description: A CloudNativePG Cluster has one instance and no backup. The agent must report both, state that the stated 5 minute RPO and 2 hour RTO cannot be met, and propose a design without applying it. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent flags instances: 1, the missing WAL archive and base backups, the missing ScheduledBackup and off-site copy, says the stated RPO/RTO are not met, proposes a plan including a restore drill, and runs no cluster or cloud command.
tags: [high-availability, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Check db/cluster.yaml against the requirement in README.md and tell me what is missing and what you would change. This is the production definition, so only propose changes.
