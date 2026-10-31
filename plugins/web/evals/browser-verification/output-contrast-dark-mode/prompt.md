---
description: "Contrast question in dark mode. Run with --scaffold --allow-tools Bash Write on a machine with Playwright browsers installed."
expected_outcome: Measures the muted text in dark mode in a headless browser (dark mode set through the page's own theme storage), reports a numeric ratio of about 3:1 and compares it with 4.5:1, and names an element screenshot path. If no browser can run, it says the result is not verified in a browser and labels any ratio as computed from the CSS source.
tags: [browser-verification, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Is the muted text on the billing cards readable in dark mode? Check it. The page is `public/billing.html`.
