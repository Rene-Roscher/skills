---
type: llm
weight: 3
---

PASS if the ADR text does not claim that the package supports only global roles; it states or at least allows that the package has a teams mode with team-scoped roles (or marks the claim as unverified), and it bases the decision on owned invariants such as the owner rule, the escalation cap on grant paths, token subsets or deactivation.
FAIL if the ADR states as fact that the package cannot scope roles per organization.
