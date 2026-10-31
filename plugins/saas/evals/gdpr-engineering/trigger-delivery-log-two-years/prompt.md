---
description: "Should trigger gdpr-engineering (validation split)."
expected_outcome: "The gdpr-engineering skill is invoked."
tags: [gdpr-engineering, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Keep notification delivery logs for two years instead of 90 days.
