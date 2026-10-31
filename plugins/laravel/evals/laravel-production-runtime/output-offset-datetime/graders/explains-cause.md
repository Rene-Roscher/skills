---
type: llm
weight: 1
---

PASS if the reply explains that the offset is lost before or during the write (Eloquent formats the value without a time zone, so the wall time is stored) and that the value must be converted to UTC before it is assigned.
FAIL if the reply blames only the database, proposes changing the database or application time zone as the whole fix, or does not say why the stored hour was wrong.
