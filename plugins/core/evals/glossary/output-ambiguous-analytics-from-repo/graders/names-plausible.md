---
type: llm
weight: 3
---

PASS if the final reply identifies the analytics tool as Plausible (plausible-tracker in package.json or src/analytics.ts), says the pricing-view event is tracked, and does not ask the user which analytics tool is meant. FAIL if it assumes Google Analytics or Google Search Console, asks which tool is meant although the repository answers it, or does not name the evidence.
