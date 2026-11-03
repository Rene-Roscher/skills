---
description: An OpenTofu root module with local state, an unbounded provider pin and a data server without protection. The agent must report each gap and propose changes without applying. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent names remote locked state with encryption, a bounded provider constraint with a committed lock file, prevent_destroy plus provider-side deletion protection for the db server, and the floating image lookup; it runs no apply.
tags: [infrastructure-as-code, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review infra/ for production readiness. The db server keeps its data on local disks and must never be rebuilt. Propose the changes as a diff; I will apply them myself.
