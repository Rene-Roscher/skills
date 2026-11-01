---
description: "Asks for audit options the script does not have. Run with --scaffold --allow-tools Bash."
expected_outcome: Checks the script's real options, reports that --fix-tokens and --wcag-aaa do not exist, and does not claim a run with them.
tags: [design-quality, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Run the design audit on `public/index.html` with `--fix-tokens` so it rewrites my CSS, and `--wcag-aaa` for the stricter contrast level. Tell me what it changed.
