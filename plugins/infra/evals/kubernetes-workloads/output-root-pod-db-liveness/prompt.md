---
description: A Deployment without securityContext, with a mutable tag, no resources, and liveness and readiness on the same endpoint that queries the database. The agent must report each gap without applying. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent proposes runAsNonRoot, readOnlyRootFilesystem, drop ALL and seccomp RuntimeDefault, an image digest, measured requests and a memory limit, and separate probes where liveness does not touch the database; it runs no cluster command.
tags: [kubernetes-workloads, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review k8s/api.yaml before it goes to production. The /health endpoint runs SELECT 1 against the database. Show the manifest changes; I will apply them.
