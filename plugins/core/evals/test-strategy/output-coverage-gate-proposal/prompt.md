---
description: A request to raise a global coverage gate to 95 percent gets a proposal built on critical modules and changed lines, with the global number informational. Needs --scaffold and --allow-tools Write.
expected_outcome: The agent writes docs/test-gate.md proposing per-module thresholds for the payments and auth modules, a changed-lines threshold, mutation testing on the critical modules, and a global percentage that is shown but not enforced. It does not simply raise the global number.
tags: [test-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Product wants the global coverage gate in ci/pipeline.yml raised from 90 to 95 percent. Write a short proposal in docs/test-gate.md for what we should do instead or additionally. Do not edit the pipeline.
