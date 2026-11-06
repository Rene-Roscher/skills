---
description: "A confirm opened from a slideover renders behind it; each overlay picks its own z-index. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Introduces one named layer scale (sheet below modal below confirm), uses the names in both components instead of raw numbers, portals the confirm to the body, makes Escape close only the confirm and return focus to the delete button, and names the test that proves the confirm is topmost.
tags: [design-quality, output]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

When I click "Delete project" in the project slideover, the confirm dialog shows up behind the slideover and I can't click it. Fix it properly.
