---
type: llm
weight: 4
---

PASS if the plan or the reply (1) states the business goal with the brief as its source (retention: customers leave because reporting still needs spreadsheets, or the month-end close metric), (2) gives a cost model with numbers for cost per dashboard view and per workspace per month at today's size and at 10x and 100x, including the paid reporting API calls against the 0.002 EUR price and the 10,000 free calls, (3) says which widgets are cached per workspace (with a TTL tied to how fresh the number must be) or precomputed, and that widgets load independently instead of in one request, (4) names a budget and what happens when it is exceeded (limit, plan entitlement, degraded widget or kill switch), (5) compares the cost with the plan prices or the 15 % margin floor, and (6) asks for approval without claiming the dashboard was built.
FAIL if the cost is only described as low or acceptable without numbers, if the paid API cost is missing, if every widget is computed in one request with no cache or precomputation, or if code was written.
