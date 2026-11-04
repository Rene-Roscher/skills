# Events, commands and long flows

Load when adding a command or event, writing a consumer, or designing a flow that crosses contexts.

## Contents

- Three kinds of message
- Naming
- Payload
- Publishing
- Consuming
- Orchestration or choreography
- Deadlines and compensation
- Worked example: checkout

## Three kinds of message

| Kind | Says | Handlers | Name | Lives | Changes |
|---|---|---|---|---|---|
| Command | "do this" | exactly one; may refuse | imperative: `ConfirmBooking` | inside a context or on its public surface | with the handler |
| Domain event | "this happened here" | zero or more, same context | past tense: `BookingConfirmed` | inside one context | freely, with the context |
| Integration event | "this happened, for others" | zero or more, other contexts | past tense, versioned: `booking.confirmed` v1 | published contract | additive only (`cross-service-contracts`) |

A domain event can be translated into an integration event by a handler in the owning context. The two are
separate types, so an internal refactor does not change the published contract.

Fowler's warning on mixing kinds: when the sender expects the receiver to act, it "ought to use a command message
to show that intention, but styles the message as an event instead".

## Naming

- The name is a glossary term plus a past-tense verb that says what happened in the business: `BookingConfirmed`,
  `HoldExpired`, `InvoiceSent`, `PaymentSettled`.
- Refused: `BookingUpdated`, `InvoiceChanged`, `CustomerSaved`, `OrderModified`, and names that only carry a
  technical step (`BookingProcessed`).
- Two different business changes are two events. "Dates moved" and "guest count changed" are
  `BookingRescheduled` and `BookingGuestsChanged`, not one `BookingUpdated` with a diff. A qualifier between the
  aggregate and the verb (`GuestsChanged`) is acceptable when it names the business fact.

## Payload

- Identity: event ID (unique, used for deduplication), event type, version for integration events, occurred-at,
  tenant reference, aggregate ID. External IDs only (`dual-key-identifiers`).
- Facts the consumers need, including decisions the owner made (`refundDue: true`, `amountDue`), so consumers do
  not recompute them.
- Not the whole row, not internal status codes the owner may rename, no personal data a consumer does not need.

## Publishing

- The root records the event during the command; the application service saves the aggregate and the event in
  one transaction (outbox row) or dispatches after commit.
- Microsoft's guide on integration events: they "should occur only if the entity is successfully persisted".
- In-process domain event handlers that must be atomic with the change may run before commit in the same
  transaction; handlers that call anything outside the database run after commit.
- Relay, retries and lag alerts follow `async-reliability`.

## Consuming

- Idempotent by event ID: claim the ID in the same transaction as the effect; a duplicate is a success.
- Tolerant of order: compare the aggregate version or occurred-at; drop an older event.
- Acts on facts from the payload; reads the owner's public surface for missing data rather than its tables.
- Never publishes a reply that the producer waits for. If the producer needs an answer, it is a command.

## Orchestration or choreography

| Situation | Use |
|---|---|
| One event, one or two independent reactions, no compensation | choreography: each consumer subscribes |
| Three or more steps, an order between them, a deadline or a compensation | orchestration: a process manager |
| A flow someone must be able to inspect ("where is checkout 4711 stuck?") | orchestration |

The saga pattern describes both: "Choreography - each local transaction publishes domain events that trigger
local transactions in other services" and "Orchestration - an orchestrator (object) tells the participants what
local transactions to execute". A process manager "maintain[s] the state of the sequence"; its cost is a central
component that knows every participant.

Process manager shape: a table `checkout_flows` with flow ID, current step, deadline of the current step, the IDs
it collected, and status (`running`, `completed`, `compensating`, `failed`, `timed_out`). It reacts to events and
deadlines, and sends commands. It holds no business rule of the participants.

## Deadlines and compensation

- Each step has a deadline stored with the flow. A scheduled sweep or delayed message fires it; the handler checks
  that the step is still pending before acting.
- Each completed step that a later failure invalidates has a compensating command: release the hold, void the
  invoice, refund the payment. Compensation is a business action with its own idempotency, not a database
  rollback; the saga has no "automatic rollback".
- A step whose outcome is unknown (timeout after the call went out) is reconciled before compensating, so a
  payment is not refunded that never settled.
- Tests: advance the clock past each deadline; kill the process between steps and restart; deliver every event
  twice.

## Worked example: checkout

Booking checkout: place hold (Availability), charge (Payments), confirm (Booking), send confirmation
(Notifications).

1. `CheckoutFlow` starts on `CheckoutRequested`, sends `PlaceHold`, deadline 30 s.
2. On `HoldPlaced`, sends `ChargePayment` with the flow ID as idempotency key, deadline 10 min.
3. On `PaymentSettled`, sends `ConfirmBooking`. On `PaymentFailed` or the deadline, sends `ReleaseHold` and marks
   the flow failed.
4. On `BookingConfirmed`, the flow completes. Notifications reacts to `BookingConfirmed` by choreography; it is
   not a step, because its failure undoes nothing.
5. If `ConfirmBooking` is refused (`HoldExpired`), sends `RefundPayment` and `ReleaseHold`, marks the flow
   compensated.
