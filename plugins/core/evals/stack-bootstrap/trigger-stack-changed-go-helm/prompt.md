---
description: "Should trigger stack-bootstrap (validation split). Run with --ablation none."
tags: [stack-bootstrap, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We added a Go service and a Helm chart to the monorepo. Update which agent plugins are enabled here.
