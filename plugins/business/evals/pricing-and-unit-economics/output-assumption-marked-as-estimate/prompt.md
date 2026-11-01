---
description: A margin that depends on an assumed cost must be reported as an estimate, with what would measure it. Needs --scaffold and --allow-tools Bash Write.
expected_outcome: The agent computes the margin, labels it an estimate because the SMS price is marked as an assumption, and names how to measure the real price.
tags: [pricing-and-unit-economics, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

What margin does the team plan in docs/product/model.json have? I want to put the number in the investor deck.
