---
description: When code disagrees with a lesson the agent follows the code, says so, and fixes or deletes the lesson. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent finds the npm lesson, sees pnpm-lock.yaml and the packageManager field, uses pnpm and not npm, reports the drift, and corrects the lesson in place with date and reason or deletes it with its index line.
tags: [learning-loop, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Add dayjs as a dependency of this project.
