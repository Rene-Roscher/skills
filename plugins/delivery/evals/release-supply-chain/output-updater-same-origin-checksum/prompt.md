---
description: "A self-updater that trusts a checksum from the download origin. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The review flags the same-origin checksum as integrity only, requires signature verification against a key compiled into the binary, atomic replace with the previous binary kept, health check with automatic rollback, and refusal of older versions."
tags: [release-supply-chain, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Review `internal/update/update.go` before we ship this agent to customer servers.
