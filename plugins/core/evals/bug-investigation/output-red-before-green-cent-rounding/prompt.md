---
description: "Red before green: totals off by one cent come from float math and rounding. The fixture has an existing test file, so the test change is expected as an Edit. Needs --scaffold --allow-tools Edit Write Bash."
expected_outcome: "A failing test is added before src/cart.py changes, tests run at least twice, the reply names the trigger, says the test failed without the fix, and reports a sibling search."
tags: [bug-investigation, output]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Users report totals off by one cent for some carts. Fix it. Tests run with: python3 -m unittest discover -s tests -t .
