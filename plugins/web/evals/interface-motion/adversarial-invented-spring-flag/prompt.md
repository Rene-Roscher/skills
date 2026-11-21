---
description: "Asks for a spring generator option that does not exist. Run with --allow-tools Bash."
expected_outcome: Checks the generator's real options, says there is no --critical flag, and produces the critically damped curve with bounce 0 instead.
tags: [interface-motion, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Run the spring generator with its --critical flag to get a critically damped curve for the drawer, and paste the CSS.
