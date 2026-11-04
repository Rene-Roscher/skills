# When DDD pays

Load when deciding between a plain CRUD module and a modelled context, or when someone proposes event sourcing,
CQRS or a message broker.

## Contents

- Depth per context
- Signals
- Event sourcing, CQRS and brokers
- ADR skeleton
- Worked example: invoicing app

## Depth per context

Depth is chosen per context, not per application. One codebase usually has one or two modelled contexts and
several CRUD modules.

| Depth | What it contains | Fits |
|---|---|---|
| CRUD module | model, validation, one service per write, list and show queries | settings, reference data, tags, simple admin screens |
| Modelled context | aggregates with invariants on the root, domain events, a public surface | pricing, booking rules, invoicing and dunning, entitlement checks |
| Modelled context with an anti-corruption layer | the above plus a translation layer to a vendor or legacy model | payments, accounting export, a legacy booking engine |

A CRUD module still lives inside a context, still uses the glossary terms and is still fenced by the arch test.
It does not get repositories, factories, value objects or events for their own sake.

## Signals

Model the context when two or more of these hold:

- A use case is refused for a business reason (a booking past its cancellation window, an invoice already sent).
- The same rule must hold for several entry points (UI, API, import, console).
- Domain experts use words the code does not have yet, or the code uses words they do not.
- Several teams change the context, or it is expected to live for years.
- A state machine has guards (draft, sent, paid, overdue, written off).

Stay CRUD when every use case is store, list, show, edit or delete, and validation is the only rule.

## Event sourcing, CQRS and brokers

These are storage and integration choices, not part of "doing DDD". Each needs an accepted ADR before code.

| Choice | What it costs | Ask before accepting |
|---|---|---|
| Event sourcing | the event store becomes the source of truth; rebuilding state is slow with many events; replays call external systems unless gateways are switched off; "very hard to retrofit" and as hard to remove | Is there a need for full history, retroactive correction or temporal queries that an audit table does not meet? |
| CQRS with a separate read store | two models, sync lag, a projection to operate | Is there a measured read load or read shape the write model cannot serve with an index or a view? |
| Message broker | a new failure domain, at-least-once delivery, lag to monitor, a contract per topic | Do consumers run in another process or service today? Inside one app, after-commit jobs or an outbox table usually suffice (`async-reliability`). |

Fowler on CQRS: "for most systems CQRS adds risky complexity" and it "should only be used on specific portions of
a system". A request to add all three to a small CRUD app is answered with the ADR questions, not with code.

## ADR skeleton

```markdown
# ADR-NNN: [event sourcing | CQRS | broker] for [context]

Status: proposed
Problem: [what fails today, with numbers or a concrete case]
Options considered: [plain tables plus audit log | index or view | after-commit jobs | outbox] and why each fails
Decision: [choice], scoped to [context], not the whole system
Trade-off: [what we give up: operations, lag, failure domain, retrofit cost]
Exit: [how we would remove it, and the signal that tells us to]
Owner: [person or team]
```

## Worked example: invoicing app

An invoicing app has Customers, Invoices, Payments and Settings.

- Settings (company address, logo, default payment term) is a CRUD module: one form, validation, no events.
- Invoicing is modelled: an `Invoice` aggregate with lines, the rule "a sent invoice is never edited, only
  credited", and events `InvoiceSent`, `InvoiceCredited`.
- Payments sits behind an anti-corruption layer that maps the payment provider's statuses into `PaymentSettled`
  and `PaymentFailed` in the Payments context's own terms.
- Nobody proposes event sourcing: the audit need is met by an append-only `invoice_events` table written in the
  same transaction.
