---
description: "Should trigger service-boundaries (train split)."
expected_outcome: "The service-boundaries skill is invoked."
tags: [service-boundaries, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Rust service needs to read config that Laravel encrypts. Can we just share APP_KEY?
