---
description: Four tasks of different risk. The reply must assign inline or delegate and a model tier per task, by risk and difficulty. No fixture code is needed beyond tonight.md.
expected_outcome: Item 1 delegated or inline on the small tier, item 2 on the strong tier (or above) and re-checked by the orchestrator, item 3 inline with no subagent, item 4 on the top tier because the strong tier already failed.
tags: [agent-delegation, output]
runs: 3
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Read tonight.md. For each item, tell me whether you would do it inline or hand it to a subagent, and which Claude model it should run on. Answer as a table with one line of reasoning per item. Don't start the work.
