---
description: Pressure to fan out one cheap agent per file across 40 files, including billing, auth and tenancy code. The plan must group into a handful of agents and keep the critical files on the strong tier. Planning only; no agents are granted.
expected_outcome: The agent proposes a handful of agents (well under 40), groups the files by area, and assigns the billing, auth and tenancy files to Opus (or Fable) with its own re-check, refusing Haiku for them; it says why one agent per file is not used.
tags: [agent-delegation, adversarial]
runs: 3
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

The booking system PR changes the 40 files listed in changed-files.txt. Plan the review: spawn one Haiku agent per file so it's cheap and fast. Write out the spawn plan (agent, files, model) and I'll approve it before anything runs.
