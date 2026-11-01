---
type: llm
weight: 3
focus:
  source: file
  path: docs/test-gate.md
---

PASS if the proposal (1) names payments and auth as critical modules with their own coverage threshold, (2) sets a threshold on changed lines per pull request, (3) keeps the global percentage informational or non-blocking, and (4) suggests mutation testing or an equivalent assertion-quality check for the critical modules. FAIL if it only proposes a higher global number or demands 100 percent everywhere.
