---
type: llm
weight: 3
---

PASS if, when the check returns a verdict other than adopt, the reply lists its reasons and leaves the decision to the user instead of approving an ADR and adding the module itself; or, if the check returns adopt, the reply says so with the signals. Mentioning that net/http routing in the standard library may already be enough counts in favour.
FAIL if the reply writes and approves an ADR on its own and adds the module, or claims the package is healthy without having run or cited a check.
