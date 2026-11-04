---
type: llm
weight: 3
---

PASS if the reply declines to have Billing query the orders table directly, explains that Orders owns the table and the schema would become an unversioned contract, proposes a query interface owned by Orders (or an event-fed copy or a published view), and says the new Orders-to-Billing edge needs a context map row and an arch rule, or the owner's decision.
FAIL if the reply adds DB::table('orders') or an Orders model import in Billing as the solution.
