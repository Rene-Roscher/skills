---
type: llm
weight: 3
---

PASS if the reply advises against a single generic BookingUpdated event, explains that consumers would have to diff the payload to learn what happened, proposes one specific past-tense event per business change, and limits the payload to the facts Invoicing needs instead of the whole row.
FAIL if the reply accepts BookingUpdated with the full row as the design.
