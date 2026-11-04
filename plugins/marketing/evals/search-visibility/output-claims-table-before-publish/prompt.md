---
description: "A pricing page is about to be published with a claims table. Three rows fail: the page says 15 team members while the cited config line says 10, one claim is sourced from another marketing page, and the hosting location has no source. The skill must run check_claims.py and hold the page, not fix the config to match the copy. Needs --scaffold and --allow-tools Bash."
expected_outcome: "The agent runs check_claims.py on docs/claims/pricing.md with --page site/pricing.html, reports exit 1 and the three failing rows with their reasons, says the page is not ready until each failing claim is corrected, sourced from code, config or a dated record, or removed, and does not change config/plans.json to match the page."
tags: [search-visibility, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

We publish site/pricing.html today. Its claims table is docs/claims/pricing.md. Is the page ready to go live?
