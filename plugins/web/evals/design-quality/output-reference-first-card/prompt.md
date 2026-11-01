---
description: "Add a card to an existing page. Run with --scaffold --allow-tools Bash Write Edit."
expected_outcome: Reads the existing settings page and tokens first, reuses the existing card markup and token variables, and adds no new colour, gradient or off-token value.
tags: [design-quality, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

Add a "Payment reminders" card to `public/settings.html` with a toggle and a days-before-due field.
