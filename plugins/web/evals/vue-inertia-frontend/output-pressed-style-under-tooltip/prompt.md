---
description: "Pressed style lost because a tooltip trigger wraps the toggle. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Explains that the tooltip trigger and the toggle both set data-state on the merged element, switches the pressed style to the aria-pressed attribute, and keeps the tooltip.
tags: [vue-inertia-frontend, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Since I added the tooltip, `PinToggle.vue` no longer shows the dark pressed style, although the value saves correctly. Fix it.
