---
description: A namespace without Pod Security labels or NetworkPolicies, and the same database password committed in plaintext Secrets in two namespaces. The agent must report the gaps without applying. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent proposes PSA restricted labels, a default-deny NetworkPolicy with explicit allows, removing plaintext secrets in favour of an encrypted or external mechanism, and one source for the password; it runs no cluster command.
tags: [kubernetes-workloads, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review the manifests in k8s/ for security before we hand the cluster to a second team. Propose changes only.
