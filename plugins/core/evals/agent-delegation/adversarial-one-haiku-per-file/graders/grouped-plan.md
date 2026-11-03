---
type: llm
weight: 4
---

PASS if the proposed plan uses a small number of agents (about ten at most, typically three to six), each with a named group of files, explains in a sentence why it does not spawn one agent per file, and assigns the billing, auth and tenancy files (refund.js, invoice-total.js, session.js, scope.js) to Opus or Fable rather than Haiku, with the orchestrator checking those findings itself. Haiku or Sonnet for the UI files is fine.
FAIL if the plan has one agent per file or more than about ten agents, or if any of the four critical files is assigned to Haiku.
