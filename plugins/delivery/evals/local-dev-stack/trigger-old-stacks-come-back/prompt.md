---
description: "Should invoke local-dev-stack (validation split). Run with --ablation none."
expected_outcome: "The local-dev-stack skill is invoked."
tags: [local-dev-stack, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

After every reboot the dev containers of three old projects start again and eat my RAM. Fix the compose setup of this project so it doesn't add to that.
