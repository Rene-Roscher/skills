---
description: A commit made by the agent must carry no tool attribution, session link, emoji or filler. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent changes the tax rate, stages only that file, commits with a plain imperative subject and a why body, and writes no trailer or credit line naming a tool.
tags: [commit-hygiene, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Change the tax rate in src/tax.js to 0.20 because the rate changed on 1 January, and commit it.
