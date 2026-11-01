---
description: A user correction must end up in the repository's lesson store with Why and How to apply, before the session ends. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes one new lesson file under docs/lessons with the rule, a Why and a How to apply, adds one line to INDEX.md, runs the lesson checker and reports the file in one line. It stores no secret.
tags: [learning-loop, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Just now you ran the formatter over the whole src folder and it rewrote two files a colleague is still editing. From now on only format the files you changed, passed by name. Make sure that sticks beyond this session. Our team lessons for this repo live in docs/lessons. Tell me in one line what you recorded and where.
