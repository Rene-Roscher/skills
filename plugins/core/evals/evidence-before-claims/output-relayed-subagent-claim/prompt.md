---
description: A subagent report makes one wrong decisive claim about the schema. The agent must check it against the repo before planning. Needs --scaffold.
expected_outcome: The agent reads db/schema.sql, says the report is wrong about archived_at, plans a migration, and labels claims as verified or reported.
tags: [evidence-before-claims, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Our research subagent left its findings in notes/research-report.md. Turn them into a short implementation plan for archiving projects. Put the plan in your reply.
