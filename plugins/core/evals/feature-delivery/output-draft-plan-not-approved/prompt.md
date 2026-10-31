---
description: "Entry gate: a draft plan with two unanswered decisions must stop the build. Needs --scaffold --allow-tools Edit Write Bash."
expected_outcome: "No source file is created or edited. The reply says the plan is a draft or not approved and names the two open decisions."
tags: [feature-delivery, output]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Implement the plan in docs/plans/2026-01-10-exports.md.
