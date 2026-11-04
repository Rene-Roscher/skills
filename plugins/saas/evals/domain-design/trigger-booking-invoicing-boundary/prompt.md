---
description: "Should trigger domain-design (validation split)."
expected_outcome: "The domain-design skill is invoked."
tags: [domain-design, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our booking app is getting messy. How should we split Booking and Invoicing into modules, and how should they talk to each other?
