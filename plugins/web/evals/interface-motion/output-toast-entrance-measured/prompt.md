---
description: "Asks for proof that a toast entrance overshoots at most 5 % and nothing around it moves. Run with --scaffold --allow-tools Write Edit Bash."
expected_outcome: Writes a check that samples the toast every frame in Chromium, Firefox and WebKit headless, also under reduced motion, computes the overshoot in percent and the layout shift of the neighbours in px, and reports numbers instead of a look.
tags: [interface-motion, output]
runs: 3
max_turns: 18
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Prove that the "Booking saved" toast overshoots by at most 5 % when it comes in, and that nothing around it moves. Write the check.
