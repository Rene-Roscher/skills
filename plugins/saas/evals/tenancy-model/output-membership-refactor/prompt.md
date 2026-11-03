---
description: "Single-tenant users table must become memberships. Needs --scaffold."
expected_outcome: "The reply adds a membership table unique on organization_id and user_id, keeps the owner as a pointer on the organization, moves existing users into memberships, and removes organization_id and role from users in a later step."
tags: [tenancy-model, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Users must be able to belong to several organizations with a different role in each. Propose the schema change, the migration steps for existing data and the tests. Reply with code; do not write files.
