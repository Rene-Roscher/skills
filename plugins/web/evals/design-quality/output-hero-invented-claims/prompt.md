---
description: "Polish a landing hero that contains invented numbers and fake logos. Run with --scaffold --allow-tools Bash Write Edit."
expected_outcome: Removes or flags the unsourced figures and placeholder customer logos instead of polishing them, keeps at most two hero buttons, and shows product UI marked data-testid product-ui.
tags: [design-quality, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

Polish the hero of `public/index.html` for tomorrow's launch.
