---
description: "A card that springs back restarts the drag at the pointer when grabbed mid-flight. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Reads the offset on screen in pointerdown, stops the transition in the same handler and continues the drag from that offset, so nothing jumps; names a test that presses the card shortly after release.
tags: [interface-motion, output]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

If I grab the card again while it is still springing back, it jumps to where my finger is. Fix it.
