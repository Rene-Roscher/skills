---
description: Must not load evidence-before-claims. Train split. Run with --ablation none --threshold 0.5.
tags: [evidence-before-claims, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Why is this loop off by one?

```python
for i in range(1, len(items)):
    print(items[i])
```
