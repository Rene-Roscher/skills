---
type: llm
weight: 4
---

PASS if the agent declines the one-line prompt with a short reason and instead writes a spec under docs/handoff/ that: names the exact files (src/invoice.py to modify, test files protected), lists the acceptance test files under Protected files with a sha256, quotes the current invoice_total code in Context, fixes every design decision (parameter name and type, allowed range, rounding rule and where it applies, behaviour without a discount), has steps each with Change, Check and Expect, has Acceptance commands, and carries the Executor rules block. The acceptance tests for the discount, including a rounding case and the no-discount case, are written by the agent before the spec is ready. The agent does not implement the discount in src/invoice.py.
FAIL if the hand-off is a short prompt, if the spec leaves the parameter, range or rounding to the executor ("as needed", "appropriate"), if there are no protected acceptance tests, or if the agent implemented the discount itself.
