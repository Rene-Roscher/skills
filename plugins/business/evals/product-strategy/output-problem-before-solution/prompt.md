---
description: An idea written as a solution in the README must come back as a problem statement without product, feature or technology words. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes docs/product/brief.md whose Problem section says who, in which situation, what they do today and what it costs, without naming the app, dashboard, notifications or AI. It runs the brief checker and writes no application code.
tags: [product-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

The idea is in README.md. Before we build anything, frame it in docs/product/ for the shift planner.
