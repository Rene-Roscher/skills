---
type: llm
weight: 3
---

PASS if both hold: (1) the reply lists a test that injects each of the three failures (provider timeout, job delivered twice, worker dies between the credit note and the provider call) and says what each asserts; (2) it requires proof that the tests on the refund calculation can fail, by a mutation run on the changed code with surviving mutants treated as missing assertions, or by breaking the guards on purpose and seeing a test fail.
FAIL if the reply treats a green suite or a coverage percentage as enough, lists fewer than three injected-failure tests, or asks the owner to read the code instead.
