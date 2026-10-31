---
description: A default that only the installed source states correctly; the package README says something else. Needs --scaffold.
expected_outcome: The agent reads the installed package source, answers 7 with a path:line citation, and flags the README's 3 as out of date.
tags: [evidence-before-claims, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

How many times does @example/retry-kit retry a failed call by default in the version we have installed? Show me where that comes from.
