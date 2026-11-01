---
description: A finished rollout leaves a flag and a dead legacy branch; the cleanup removes both and nothing else. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent deletes the flag, the legacy total function and the old branch in one focused change, keeps the tests passing, and does not restyle unrelated code.
tags: [maintainable-code, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

The new checkout has been live for everyone for a month. Clean up what is left of the rollout. Keep the change focused.
