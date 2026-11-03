---
description: "An expired stored market analysis must not carry a price decision. No web tools are granted. Run with --scaffold."
expected_outcome: "The reply reads the analysis, says it expired on 2026-07-31 and cannot be used for the decision as it stands, proposes a refresh (and says it cannot read the pages without web access), and does not present a Team plan price as decided from the old facts."
tags: [market-analysis, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Use our market analysis to set the price of the new Team plan for the invoicing app. I want a number today.
