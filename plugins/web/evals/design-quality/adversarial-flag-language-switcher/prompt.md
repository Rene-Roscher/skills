---
description: "A language switcher with country flags, phrased so emoji flags are the quickest answer. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Builds the switcher without emoji flags, using inline SVG flags or language names as text, and says why emoji flags are not used (platform rendering, Windows shows two letters).
tags: [design-quality, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a language switcher with the country flags for German, English and French to the header in `public/index.html`. Keep it quick, no new files or dependencies.
