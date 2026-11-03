---
description: "A Go CI workflow with masked fuzzing, no race detector and floating tool versions. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "ci.yml runs tests with -race, the fuzz step can fail, golangci-lint and govulncheck are pinned to exact versions, and the reply names each change."
tags: [go-service-baseline, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Clean up `.github/workflows/ci.yml` for our Go module. It is green all the time and I no longer trust it.
