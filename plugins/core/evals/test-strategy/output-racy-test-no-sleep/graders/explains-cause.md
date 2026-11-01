---
type: llm
weight: 2
---

PASS if the reply names the cause: the test sleeps a fixed 50 ms while the job takes a random time up to 80 ms, so the assertion can run before the result exists. FAIL if it blames the environment or only says it added a retry or a longer sleep.
