---
description: "New permission in a Laravel fixture with a typed permission enum. Needs --scaffold."
expected_outcome: "The reply adds a reports.export case to the enum, protects the route by referencing the enum member, and tests owner with no roles (allowed), member without the permission (denied) and deactivated member (denied)."
tags: [authorization-rbac, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a permission `reports.export` and protect `GET /reports/export`. Reply with the code and tests; do not write files.
