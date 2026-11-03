---
description: "Baseline request with no API credentials on the machine. The skill must run its script, get no access, report nothing as measured and hand the owner safe setup steps. Needs --scaffold and --allow-tools Bash Edit Write."
expected_outcome: "The agent runs measure.py, which exits 3 for lack of credentials. The reply says no numbers were measured, names the setup per source (read-only service account added as a user on the property, Bing API key, Plausible Stats API key on a plan that includes it) stored in mode-600 files or environment variables outside the repo, and presents no click, impression, position or visitor figures. It may create docs/growth/changes.md for the redesign."
tags: [search-measurement, output]
runs: 3
max_turns: 20
timeout_seconds: 500
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

We redesign the pricing page next week. Take a baseline of our search and traffic numbers now, so we can tell afterwards whether the redesign helped. The property details are in the README.
