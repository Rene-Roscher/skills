---
description: "New tag release workflow for an invoicing service with an existing ci.yml. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "release.yml has permissions {} or contents read at top level, write scopes only on the publishing or deploy job, a needs chain to the tests, timeouts on every job, no tag-only action refs, tag values reaching the shell only through env, and release concurrency that never cancels."
tags: [github-actions-hardening, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add `.github/workflows/release.yml` that builds our Docker image on `v*` tags, pushes it to GHCR and deploys it with `kubectl set image`. The existing `.github/workflows/ci.yml` has a `test` job.
