---
type: llm
weight: 2
---

PASS if the reply says that `product_id` is checked against the current team (tenant), so a product ID that belongs to another team fails validation the same way an unknown ID does.
FAIL if the reply validates `product_id` with an unscoped exists check, or does not mention the team or tenant at all.
