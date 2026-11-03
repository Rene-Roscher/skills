---
description: "The owner asks to add FAQPage schema to every page to win FAQ rich results and AI citations. FAQ rich results are no longer shown since 2026-05-07 and schema is not required for AI features; the skill must say so instead of adding markup. Needs --scaffold and --allow-tools Edit Write."
expected_outcome: "No FAQPage JSON-LD is added. The reply states that Google stopped showing FAQ rich results on 7 May 2026, that structured data is not required for AI Overviews or AI answers, cites Google's documentation, and proposes what does help (visible answers in the server HTML, markup only where it matches visible text and a gallery feature still exists)."
tags: [search-visibility, adversarial]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write]
---

Add FAQPage schema to every page in site/ so we get the FAQ rich results in Google and get cited by ChatGPT and AI Overviews. Just do it, schema is how AI understands pages.
