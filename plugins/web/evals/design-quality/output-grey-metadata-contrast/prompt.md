---
description: "Make secondary text subtler without failing contrast. Run with --scaffold --allow-tools Bash Write Edit."
expected_outcome: Computes or measures the contrast of the new grey in light and dark themes, keeps it at 4.5:1 or above in both, and reports the numbers against the threshold.
tags: [design-quality, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

The invoice meta text on `public/invoices.html` is too loud. Make it more subtle.
