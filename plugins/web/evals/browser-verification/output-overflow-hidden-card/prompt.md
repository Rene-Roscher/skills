---
description: "Overflow question where the overflow is clipped by an overflow-hidden card. Run with --scaffold --allow-tools Bash Write on a machine with Playwright browsers installed."
expected_outcome: Measures at 375 px in a headless browser, checks containers including the overflow-hidden card, reports the table clipped by about 211 px with the number and an element screenshot path. If no browser can run, it says the result is not verified in a browser.
tags: [browser-verification, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Does anything overflow horizontally on `public/invoices.html` at 375 px wide? Give me a yes or no.
