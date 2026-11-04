# Contexts and the context map

Load when adding a context or an edge between contexts, writing `docs/CONTEXT-MAP.md`, choosing a relationship
type, or building an anti-corruption layer.

## Contents

- Finding a context
- Module layout
- Context map file
- Relationship types
- Data ownership
- Anti-corruption layer
- Worked example: booking system

## Finding a context

A context boundary sits where a word changes meaning or a rule changes owner. Fowler's example: "meter" meant
subtly different things to different parts of one utility. In a booking system, "Booking" in Booking is a
reservation with a hold and a confirmation; in Invoicing it is only a billable reference with a price. Two
meanings, two contexts, two glossary rows.

Signals for a new context: a separate team, a separate glossary meaning, a rule set that changes for different
reasons, a vendor model that must not leak. A new context is the owner's decision; propose it, do not create it.

## Module layout

Same shape in every stack: one top-level folder or namespace per context, a public surface, a private interior.

| Stack | Context root | Public surface | Private interior |
|---|---|---|---|
| Laravel | `app/Domains/Booking` | `Contracts\`, `Events\`, application services | `Models\`, `Policies\`, internal actions |
| Go | `contexts/booking` | the package `contexts/booking` | `contexts/booking/internal/...` (compiler-enforced) |
| TypeScript | `src/contexts/booking` | `index.ts` | `src/contexts/booking/internal/` |

## Context map file

`docs/CONTEXT-MAP.md`, one row per pair that talks. The arch test's allowed edges are generated from or diffed
against this table.

```markdown
| upstream | downstream | relationship | mechanism | contract | enforced by |
|---|---|---|---|---|---|
| Booking | Invoicing | customer/supplier | integration event `BookingConfirmed` v1 | contracts/booking-confirmed.md | tests/Arch/ContextsTest.php |
| Payments provider | Payments | anti-corruption layer | HTTPS API and webhooks | adapter contract tests | arch rule: SDK only in Payments\Provider |
| Availability | Booking | partnership | call `AvailabilityQuery` | interface in Availability\Contracts | tests/Arch/ContextsTest.php |
```

Rules for the table: upstream is the side whose model the other adapts to; every edge in code has a row; a row
without an enforcing test is a gap to report.

## Relationship types

From Evans' DDD Reference, in the words that matter for a decision:

| Type | Use when | Cost |
|---|---|---|
| Partnership | the two contexts "succeed or fail together" | joint planning, interfaces evolve together |
| Shared kernel | a small subset of the model is shared on purpose | "Keep this kernel small"; changes need both teams |
| Customer/supplier | downstream needs shape the upstream's plan | upstream budgets downstream work; joint acceptance tests |
| Conformist | the upstream will not adapt and its model is good enough | downstream "slavishly" adopts the upstream model |
| Anti-corruption layer | the upstream model is foreign, poor or a vendor's | a translation layer in the downstream |
| Open host service with published language | many consumers need the same access | a documented, versioned protocol owned by the upstream |
| Separate ways | integration costs more than it brings | duplication of small features |

## Data ownership

- Each table belongs to exactly one context. Record it: a `tables.php`/`tables.go`/`tables.ts` map, or a comment
  block in the migration folder per context.
- Another context reads through, in order of preference: the owner's query interface (same process), a local copy
  fed by the owner's events, or a view the owner publishes and versions like an API.
- A cross-context join for a report is a read model owned by the reporting context, fed by events, or a view the
  owner publishes. It is not a join in the consumer's code.
- Foreign keys across contexts are a coupling choice. In one database they keep integrity but block moving a
  context out later; record the choice in the map's row.

## Anti-corruption layer

- Owned by the downstream context, inside its folder, named after the capability (`PaymentGateway`), not the
  vendor.
- Translates in both directions: vendor status codes into the context's terms, the context's commands into vendor
  calls. Vendor names and enums stop at the layer; they may appear in the glossary's `aliases` column with the
  note that only the layer uses them.
- Interface, fake, contract tests and exit plan follow `build-vs-buy`.
- A legacy system gets the same treatment: the new context never reads the legacy tables directly.

## Worked example: booking system

Contexts: Availability (rooms, calendars), Booking (holds, confirmations, cancellations), Invoicing (prices,
invoices), Notifications (mails and SMS, CRUD-level).

- Booking calls Availability through `AvailabilityQuery::freeSlots()`; it never queries `calendar_slots`.
- Booking publishes `BookingConfirmed` and `BookingCancelled` with `refundDue` decided by Booking.
- Invoicing consumes both events into its own `billable_bookings` table and never imports Booking's models.
- Notifications consumes events and sends mail; it decides nothing about bookings.
- Edges, upstream → downstream: Availability → Booking, Booking → Invoicing, Booking → Notifications. In code
  the downstream imports the upstream's public surface, so Booking imports from Availability, Invoicing and
  Notifications import Booking's event types, and Booking imports neither of them.
