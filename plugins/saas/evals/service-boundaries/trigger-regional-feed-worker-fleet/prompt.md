---
description: "Should trigger service-boundaries (train split)."
expected_outcome: "The service-boundaries skill is invoked."
tags: [service-boundaries, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Design a worker fleet that fetches partner price feeds from eight regions and reports back to the app.
