# Blast radius

## Classes with examples

| Class | Example |
|---|---|
| P0 leak | In an invoicing app, changing the invoice ID in the URL shows another company's invoice. |
| P0 leak | A project tool's realtime channel delivers task updates to members of a different workspace. |
| P0 leak | A booking system's export contains bookings of other venues. |
| P0 loss or money | A retry charges a card twice; a migration overwrites a column with nulls; an SMS reminder is sent ten times. |
| P0 loss or money | A refund creates two credit notes for the same payment. |
| P1 core path | Sign-in loops on one browser; checkout fails for one payment method; bookings cannot be created. |
| P2 partial | The CSV export fails for empty lists; one settings page errors; a filter returns nothing. |
| P3 cosmetic | A label is cut off; a deprecation warning fills the log; a tooltip shows the wrong date format. |

Signals that raise the class:

- Any second tenant's data in a response, a file, a mail, a webhook or a log a customer can read: P0 leak.
- Money, invoices, credits or paid messages involved: at least P0 loss or money if amounts are wrong.
- Many tenants affected, or no workaround: one class higher than the symptom alone suggests.
- Unsure: take the higher class.

The project maps these classes to its tracker labels or to another scale (SEV1 to SEV4) in its profile.

## P0: what to do

1. Stop changing code for a moment. Write the message to the owner first.
2. Quantify with read-only means: tracker counts, logs, and queries on a replica if the owner approves. Count
   tenants, users, records and amounts. Do not export the affected records themselves.
3. Preserve evidence: event IDs, log queries, the request that showed the problem.
4. Work locally on the fix and its regression test while waiting.
5. Leave production, customer contact and any disclosure decision to the owner.

Never on your own for a P0: edit production data, deploy a hotfix, rotate or revoke credentials, disable a
feature for all tenants, delete logs or events, or write to affected customers.

## Message to the owner

```text
P0 [leak | loss or money]: [one sentence: who can see or change what]
Since: [first seen, with release]          Still happening: [yes/no, last seen]
Exposure: [count] tenants, [count] users, [count] records, [amount if money]
How it was found: [tracker issue, user report, test]
Evidence: [event IDs, log query, request]
Done so far: [read-only checks, local reproduction]
Needs your decision: [containment options, for example disable the endpoint, with their effect]
```
