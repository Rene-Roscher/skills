---
description: "A marketing page requested inside the product app. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Recommends a separate public site with its own deployment, argues with failure domain or caching and SEO stability rather than PHP speed, and does not add a Pricing page to the Inertia app. If it offers to build in the app anyway, it says that deviation needs an ADR naming the trade-off.
tags: [web-architecture, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a `/pricing` marketing page to our Laravel + Inertia app, it should rank on Google.
