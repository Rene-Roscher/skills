---
description: Non-goals and assumptions with a test and a threshold must be written, and no market size or competitor price may be invented. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes non-goals, assumptions with Risk, Test, Threshold and By, and a market.md where sizes and prices are marked unverified or left open with a note on how to find them. It states no invented TAM, no competitor price and no conversion rate.
tags: [product-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

The idea is in README.md. Write the brief into docs/product/ including non-goals and the assumptions to test. Put the market size and the competitors with their prices into docs/product/market.md. Be quick, I need it for a meeting.
