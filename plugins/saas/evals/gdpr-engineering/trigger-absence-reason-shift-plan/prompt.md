---
description: "Should trigger gdpr-engineering (train split)."
expected_outcome: "The gdpr-engineering skill is invoked."
tags: [gdpr-engineering, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Store why an employee is absent from the shift plan: vacation, sick or other.
