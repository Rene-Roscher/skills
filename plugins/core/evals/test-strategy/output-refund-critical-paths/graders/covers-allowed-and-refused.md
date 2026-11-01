---
type: llm
weight: 3
focus:
  source: file
  path: tests/test_refunds.py
---

PASS if the test file contains (1) a successful refund that checks the stored entry, (2) a refund above the paid amount that is refused, (3) a refund requested by a different tenant that is refused, and (4) for the refused cases an assertion that the store is still empty or unchanged. FAIL if any of the four is missing.
