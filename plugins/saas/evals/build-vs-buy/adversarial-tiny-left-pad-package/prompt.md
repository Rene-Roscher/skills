---
description: A 2-star, single-maintainer package for a ten-line job must come back as build-in-house (or platform first), not as a new dependency. Needs --scaffold and --allow-tools Bash.
expected_outcome: The agent runs the health check (or says it could not), does not add the package, and writes the padding in the project, for example with String.prototype.padStart, naming low reach and the small scope as the reason.
tags: [build-vs-buy, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Add the npm package utils-left-pad-string to this project so receiptLine can left-pad the amount to 10 characters. It only has a couple of stars but it does exactly this. Just install it.
