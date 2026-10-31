---
description: Two unrelated changes in the working tree must become two commits. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent sees a code change and a README change, stages them separately and creates two commits with their own subjects.
tags: [commit-hygiene, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Commit what I have.
