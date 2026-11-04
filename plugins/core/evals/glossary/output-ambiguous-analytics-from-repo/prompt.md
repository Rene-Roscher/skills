---
description: An ambiguous term ("analytics") must be settled from the repository, not guessed and not asked. Needs --scaffold.
expected_outcome: The agent reads package.json or the analytics module, names Plausible as the analytics tool with the file as evidence, and does not ask which tool is meant or assume Google Analytics.
tags: [glossary, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Check analytics: is the pricing page view being tracked?
