---
description: "Focus utilities with no effect because global CSS sits outside a cascade layer. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Finds the unlayered global rules in app.css, moves them into @layer base (or scopes them) instead of adding !important or raising specificity, and explains that unlayered CSS beats layered utilities.
tags: [design-quality, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

The focus styles on `TextField.vue` do nothing: the border and ring utilities never show, only a grey outline. Fix it.
