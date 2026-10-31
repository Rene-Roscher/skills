---
description: "Should trigger service-boundaries (validation split)."
expected_outcome: "The service-boundaries skill is invoked."
tags: [service-boundaries, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Let's split billing into its own microservice.
