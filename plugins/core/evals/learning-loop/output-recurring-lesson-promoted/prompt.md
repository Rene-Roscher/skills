---
description: A lesson that fired a third time must become a guard that fails on the mistake, with the lesson shrunk to a pointer. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent builds a test that scans the migrations for float money columns, runs it red on the bad migration, fixes the migration to integer cents, runs it green, and shrinks the lesson to the rule, the Why and a pointer to the test.
tags: [learning-loop, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

A migration added a float amount column again. It is db/migrations/002_add_credits.sql and has not been applied anywhere yet. That is the third time, and the lesson docs/lessons/money-integer-cents.md obviously is not enough. Deal with it properly.
