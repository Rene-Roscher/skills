---
type: llm
weight: 2
---

PASS if the reply explains that the global rules in app.css sit outside a cascade layer and therefore win over the layered Tailwind utilities regardless of specificity, and that moving them into `@layer base` fixes it.
FAIL if the reply blames specificity alone, adds `!important`, or changes only the component.
