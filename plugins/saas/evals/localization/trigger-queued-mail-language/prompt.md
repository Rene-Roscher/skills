---
description: Should load localization. Validation split. Run with --ablation none --threshold 0.5.
tags: [localization, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Users who set their language to English still get the certificate expiry mail in German. The mail is sent from a queued job. Make it go out in the right language.
