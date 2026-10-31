---
description: "Should trigger browser-verification (validation split). Run with --ablation none."
tags: [browser-verification, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the e2e tests against the production build of the docs site.
