---
description: "A config loader that falls back to defaults on parse errors. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "config.go returns an error naming the key for unparseable values and non-positive durations instead of falling back to the default, and the reply explains why a silent default is dangerous."
tags: [go-service-baseline, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Fix `internal/config/config.go` so a misconfigured worker cannot start with wrong values.
