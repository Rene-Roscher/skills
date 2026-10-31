---
type: llm
weight: 3
---

PASS if the job's handle() does not read the organization from ambient state (the CurrentOrganization holder, the container, the session or the authenticated user) but loads it from the ID passed to the constructor, and checks before sending that the organization still exists and is not scheduled for deletion.
FAIL if handle() calls CurrentOrganization or any other ambient accessor to pick the organization, or if it sends without checking that the organization is still active.
