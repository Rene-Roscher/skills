---
description: "Should trigger service-boundaries (validation split)."
expected_outcome: "The service-boundaries skill is invoked."
tags: [service-boundaries, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Image resizing pins our PHP queue workers at 100 % CPU. Should that become a separate service?
