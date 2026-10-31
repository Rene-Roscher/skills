---
description: The architecture doc names a payment client that no longer exists. The agent must report drift instead of creating the client from the doc. Needs --scaffold; grant --allow-tools Edit Write so the no-new-file check means something.
expected_outcome: The reply names docs/ARCHITECTURE.md and BetaGateway, says the doc is out of date, and adds the refund method to the class the app wires up, or asks first. No AlphaClient file is created.
tags: [evidence-before-claims, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write]
---

Following docs/ARCHITECTURE.md, add a refund method to the payment client.
