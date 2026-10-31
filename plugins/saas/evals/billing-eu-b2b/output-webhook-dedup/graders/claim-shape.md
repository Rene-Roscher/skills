---
type: llm
weight: 3
---

PASS if the proposed dedup claims the effect atomically (insert-on-conflict or an equivalent unique-index insert that does not raise), does not keep an exists() check followed by an insert as the dedup mechanism, uses a key that includes the state transition or status being acted on (not only the payment ID), and fetches the payment from the provider API before changing state.
FAIL if the reply keeps check-then-insert as the dedup, or keys the dedup on the payment ID alone, or acts on the webhook body without fetching the payment.
