---
description: "A release workflow that publishes unsigned binaries and installs a tool by piping a script into a shell. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "release.yml signs SHA256SUMS keyless, verifies it in the same job with an exact or anchored identity and the GitHub OIDC issuer, installs syft at a pinned version with a checksum instead of a pipe into a shell, and the reply proposes release notes that start with the verify command."
tags: [release-supply-chain, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Finish `.github/workflows/release.yml` so our binaries are signed and users can verify them.
