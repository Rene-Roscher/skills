---
description: "Should trigger gdpr-engineering (validation split)."
expected_outcome: "The gdpr-engineering skill is invoked."
tags: [gdpr-engineering, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Send all new users a welcome email sequence and, two weeks later, ask them to leave a public review of us.
