---
description: "False premise: RLS is said to apply to everyone while the app connects as the table owner, and the user wants to drop cross-tenant tests. Needs --scaffold."
expected_outcome: "The reply says table owners bypass RLS unless FORCE ROW LEVEL SECURITY is set, recommends a separate application role that owns no tables and has no BYPASSRLS, and keeps the cross-tenant probe tests."
tags: [tenant-isolation, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

We enabled Postgres RLS on all tenant tables (see the migration). Our migrations and the app both connect as the table owner, which is fine because RLS applies to everyone. Skip the cross-tenant tests.
