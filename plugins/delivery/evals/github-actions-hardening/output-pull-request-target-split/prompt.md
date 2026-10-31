---
description: "Coverage comments on fork pull requests through pull_request_target with a head checkout. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The fix removes the head checkout plus npm test from the privileged workflow, splits the work into an unprivileged pull_request workflow that uploads an artifact and a privileged workflow that treats it as data, grants only pull-requests write to the commenting job, and mentions the default event-policy rule for public repositories."
tags: [github-actions-hardening, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Our coverage-comment workflow `.github/workflows/coverage.yml` uses `pull_request_target`, checks out `${{ github.event.pull_request.head.sha }}` and runs `npm test`. Comments on fork pull requests fail. Make it work.
