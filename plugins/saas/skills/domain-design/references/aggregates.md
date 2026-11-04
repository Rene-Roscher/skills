# Aggregates

Load when designing an aggregate, deciding what belongs inside it, or testing its invariants.

## Contents

- Finding the boundary
- Shape of the root
- Tests at the root
- Use case shape
- Worked example: booking

## Finding the boundary

1. Write the invariants as sentences a domain expert agrees with: "a booking holds one room for one date range",
   "a confirmed booking cannot be confirmed again", "a hold expires after 15 minutes".
2. Keep only true invariants, ones that must hold at commit. Vernon: "An invariant is a business rule that must
   always be consistent", meaning transactional consistency. A rule that may lag by seconds ("the invoice exists
   after confirmation") is eventual and goes through an event.
3. The aggregate is the smallest cluster that can enforce its true invariants on its own.
4. Anything that grows without bound (all bookings of a room, all invoices of a customer) is outside, referenced
   by ID.
5. A rule that seems to need two aggregates in one transaction is a signal: either the rule is eventual, or the
   boundary is wrong and the two are one aggregate.

## Shape of the root

- Commands are methods named in glossary terms: `confirm()`, `cancel(reason)`, `extendHold()`. No public setters
  for state that an invariant guards.
- A refused command raises a named domain error (`HoldExpired`, `AlreadyConfirmed`), never returns `false` or
  writes a flash message.
- The root records domain events in a list during the command; the application service publishes them after
  commit (`events-and-flows.md`).
- References to other aggregates are IDs (`roomId`, `customerId`), not loaded objects.
- Values without identity (date range, money) are immutable value types with their own checks. Evans: "Treat the
  value object as immutable."
- In an active-record framework, the model can be the root: put the guarded methods on the model and forbid
  direct writes to guarded columns outside it (a structural test over `->update([...'status'...])` and
  `->status =` outside the model).

## Tests at the root

One unit test per invariant, plus one per event. No HTTP, queue or database: construct the aggregate in memory.

```text
given a booking on hold since 10:00 with a 15-minute hold
when confirm() is called at 10:16
then HoldExpired is raised and no BookingConfirmed is recorded

given a confirmed booking
when confirm() is called
then AlreadyConfirmed is raised

given a booking on hold
when confirm() is called inside the hold
then the status is confirmed and exactly one BookingConfirmed with the booking ID is recorded
```

Inject the clock, so the hold test does not depend on wall time.

## Use case shape

An application service per use case (`ConfirmBookingService`, see `laravel-architecture` for the Laravel shape):

1. Load one aggregate by ID, scoped to the tenant.
2. Call one command on the root.
3. Save it in one transaction, together with its recorded events (outbox row or after-commit dispatch).
4. Return a result; never inspect the aggregate's fields to make a decision the root should make.

A service that loads a second aggregate to read a value passes that value into the command. It does not change
the second aggregate in the same transaction.

## Worked example: booking

- `Booking` (root): ID, `roomId`, `customerId`, date range, status, hold expiry. Invariants: one status
  transition at a time, confirm only inside the hold, cancel only before the start date.
- `Room` is its own aggregate in Availability. Double-booking is prevented by Availability: a unique constraint
  on `(room_id, date)` in its slot table, claimed when the hold is placed. Booking does not load all bookings of a
  room to check overlap.
- `Invoice` is an aggregate in Invoicing, created from `BookingConfirmed` after commit, not in the confirmation
  transaction.
