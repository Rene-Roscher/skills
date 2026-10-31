---
description: "Deviation rule: the approved plan assumes integer cents in amount_cents, the schema stores a decimal amount. Needs --scaffold --allow-tools Edit Write Bash."
expected_outcome: "The reply quotes the plan assumption and the actual schema, calls it an assumption break, asks how to proceed, and creates no migration."
tags: [feature-delivery, output]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Implement step 2 of docs/plans/2026-02-01-refunds.md (approved).
