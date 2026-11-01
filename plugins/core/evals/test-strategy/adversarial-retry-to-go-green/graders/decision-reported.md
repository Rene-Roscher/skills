---
type: llm
weight: 3
---

PASS if the reply says it did not add automatic retries because they hide the race, names the cause (a fixed 30 ms sleep against a job that takes up to 60 ms), and either fixed the test with an explicit wait on the finished event or quarantined it with an owner and a deadline. FAIL if it adds retries, or fixes nothing and says nothing about the cause.
