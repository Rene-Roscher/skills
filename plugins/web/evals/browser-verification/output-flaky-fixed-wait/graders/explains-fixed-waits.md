---
type: llm
weight: 2
---

PASS if the reply explains that a fixed wait keeps the test flaky (too short on a slow or loaded runner, wasted time elsewhere) and that the test now waits for the condition it asserts before counting. It may decline the 2 second wait or replace it, as long as no fixed wait remains.
FAIL if the reply adds a fixed wait, or changes the test without explaining why a fixed wait is not used.
