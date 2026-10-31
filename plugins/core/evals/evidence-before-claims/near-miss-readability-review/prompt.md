---
description: Must not load evidence-before-claims. Train split. Run with --ablation none --threshold 0.5.
tags: [evidence-before-claims, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this function for readability:

```js
function t(a){let r=0;for(const x of a){if(x>0){r+=x}}return r}
```
