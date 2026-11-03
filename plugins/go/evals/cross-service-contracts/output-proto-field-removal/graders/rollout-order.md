---
type: llm
weight: 2
---

PASS if the reply says consumers must stop reading `legacy_code` before (or independently of) the producer dropping it, and that `buf breaking` against the main branch should run as a blocking check (or explains that it will flag the removal and how the reservation is intended).
FAIL if the reply presents the removal as safe to ship to all sides at once with no mention of consumer order or a breaking-change check.
