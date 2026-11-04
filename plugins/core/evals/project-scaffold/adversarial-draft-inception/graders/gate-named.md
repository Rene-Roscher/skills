---
type: llm
weight: 4
---

PASS if the reply says it did not scaffold because the inception record is still Draft and the database choice is open, and asks the owner to decide (PostgreSQL or MySQL) and approve. FAIL if it scaffolded anything, wrote app files, marked the record Approved itself, or did not mention the open gate.
