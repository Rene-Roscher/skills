---
description: Should load learning-loop. Train split. Run with --ablation none --threshold 0.5.
tags: [learning-loop, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Remember for next time: our tests must run against the production database engine, because the in-memory one hid a migration error that broke the release.
