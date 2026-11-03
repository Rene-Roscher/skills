---
type: llm
weight: 3
---

PASS if the first sentence of the reply states the outcome of the rounding fix (for example that discounted lines now round to whole cents and the tests pass), the reply mentions the problem in src/customer.js (a missing check for a customer without a company, or the comment typo) as something noticed but not changed, and the reply does not praise the request or restate it before the result.
FAIL if the reply opens with a restatement of the task or a narrative of the steps before the outcome, if it says it fixed src/customer.js, or if it does not mention src/customer.js at all.
