---
description: Should load maintainable-code. Run with --ablation none --threshold 0.5.
tags: [maintainable-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Review my change for maintainability: it adds a new retry wrapper around our HTTP client although two other modules already retry, plus a feature flag with no owner.
