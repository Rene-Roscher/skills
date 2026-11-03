---
description: "Technical SEO audit of a built static site with four planted issues: canonical of the features page points to the home page, the hreflang pair is one-way, the pricing page has no content in the server HTML, and an old URL uses a meta refresh instead of a redirect. No web tools. Run with --scaffold."
expected_outcome: "The reply lists findings for all four issues, each with severity, URL, evidence from the file, fix and a way to verify, and does not claim ranking positions it did not measure."
tags: [search-visibility, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit the built marketing site in dist/ for technical SEO problems before we deploy. Give me the findings.
