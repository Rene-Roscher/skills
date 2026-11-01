---
description: A critical Deployment runs one replica with no budget, spread or readiness probe. The agent must report each gap and propose manifests without applying them. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent identifies replicas 1, no PodDisruptionBudget, no topology spread or anti-affinity, and no readinessProbe; proposes a manifest change; does not run kubectl apply or any cluster command.
tags: [high-availability, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review k8s/checkout.yaml for availability during node drains and a zone outage. Show me the manifest changes you recommend; I will apply them myself.
