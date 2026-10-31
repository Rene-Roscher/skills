---
type: llm
weight: 1
---

PASS if the reply says the rules went into a FormRequest instead of inline validation and gives a reason: the project's existing FormRequest convention, one place for rules that UI and API share, or that inline validation would need a recorded decision (ADR).
FAIL if the reply validates inline, or moves the rules into a FormRequest without saying why it did not follow the request for inline validation.
