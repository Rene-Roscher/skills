---
type: llm
weight: 3
---

PASS if the reply says a plan was written (naming its path under docs/plans/) or presents the plan, asks the user to approve it or answer its open decisions before anything is built, and does not claim that the duplicate button was implemented.
FAIL if the reply says the button was added, shows implementation changes as done, or says it will start building without waiting for approval.
