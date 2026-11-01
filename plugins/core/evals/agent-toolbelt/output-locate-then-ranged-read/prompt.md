---
description: A question about one function in a very large file is answered by locating it with a search and reading only the needed range. Needs --scaffold and --allow-tools Bash.
expected_outcome: The agent searches for compute_tax_rate, reads a small range around the hit instead of the whole file, and answers 0.19.
tags: [agent-toolbelt, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

In src/big.py, what does compute_tax_rate return for region DE? Do not read the whole file.
