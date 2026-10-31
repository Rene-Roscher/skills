---
description: "Should trigger gdpr-engineering (validation split)."
expected_outcome: "The gdpr-engineering skill is invoked."
tags: [gdpr-engineering, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Move file uploads to an S3 bucket in us-east-1 for lower latency.
