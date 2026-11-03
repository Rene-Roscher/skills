---
type: llm
weight: 3
---

PASS if the reply (1) computes the cost of one announcement for the largest tenant (500 x 0.08 = 40 EUR) and at 100 times that size (50,000 subscribers, 4,000 EUR), (2) explains that with tries = 5 a failure after some sends repeats SMS that already went out, (3) proposes recording each send per recipient and announcement and skipping recorded ones, (4) flags loading all subscribers into one job and proposes chunked jobs, and (5) gives path:line locations.
FAIL if the cost is not computed, the retry duplication is missed, or the fixes are generic advice without locations.
