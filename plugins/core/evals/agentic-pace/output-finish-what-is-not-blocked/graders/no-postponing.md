---
type: llm
weight: 3
---

PASS if all hold: (1) the reply says it does items 1 and 2 now, in this session; (2) it names item 3 as a decision of the owner and asks for it, with or without a recommendation; (3) it names item 4 as waiting on the payment provider and says what it prepares in the meantime, for example the handler and a test against a sample payload; (4) it does not treat the late hour as a reason to stop.
FAIL if it proposes to continue tomorrow or in a later session with item 1 or 2, calls this a good stopping point, or leaves item 3 or 4 without saying what unblocks it.
