---
description: "Should trigger eu-de-legal-baseline (train split)."
expected_outcome: "The eu-de-legal-baseline skill is invoked."
tags: [eu-de-legal-baseline, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our booking system has been sold to companies only. Next sprint we want to let individual people sign up for the monthly plan with a credit card. What has to change in the sign-up and checkout before we flip that switch?
