---
description: A why-question about a config value is answered from the git history, with a pickaxe or line-log command, and looks past a later reformatting commit. Needs --scaffold and --allow-tools Bash.
expected_outcome: The agent uses git log -S, -G or -L (or blame ignoring the reformat) and reports the reason from the commit message: the provider times out under load. It changes nothing.
tags: [agent-toolbelt, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Why is RETRY_LIMIT 5 in config.py? Find out from the repository history; do not guess.
