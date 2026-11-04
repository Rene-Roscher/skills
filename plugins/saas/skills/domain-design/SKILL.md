---
name: domain-design
description: "Applies domain-driven design where it pays and refuses it where it is ceremony: bounded contexts as modules fenced by an arch test, a context map, glossary-backed terms, small aggregates, domain versus integration events published after commit, sagas with timeouts, anti-corruption layers. Use when adding a module, event or cross-context call, or someone proposes DDD, CQRS, event sourcing or a broker. Not for wire formats."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Domain design

This skill decides how a long-lived SaaS codebase is cut into bounded contexts, how they talk, where business rules
live and which messages carry what. It applies domain-driven design where rules are rich and refuses it where a
CRUD module is enough; every rule ends in a check a reviewer or CI can run. The failure it prevents: contexts that
exist only in a diagram, rules copied into controllers and consumers, and an event store or broker that a small
app pays for every day.

## Applies when / does not apply

- Applies: adding a module, aggregate, command or event, a call or query from one module into another, a flow
  across modules, a vendor or legacy integration; someone proposes DDD, CQRS, event sourcing, a broker, a `Shared`
  module, or renames a business term.
- Does not apply: wire formats and versioning (`cross-service-contracts`), retries, outbox relay and queues
  (`async-reliability`), deploying a separate service (`service-boundaries`), Laravel folder layout
  (`laravel-architecture`), vendor admission (`build-vs-buy`), the glossary file itself (`glossary`).

## Rules

Examples use a booking system (Availability, Booking) and an invoicing app (Invoicing, Payments). Evans' DDD
Reference is https://www.domainlanguage.com/ddd/reference/; all sources verified 2026-11-04.

### Depth

- [default] Use aggregates, domain events and anti-corruption layers only in a context whose rules change with the
  business (pricing, eligibility, guarded state machines), that several teams touch, or that will live for years.
  A store-list-show context stays a CRUD module: model, validation, one service per write, no events.
  Trade-off: a CRUD module that grows rules needs a refactor later. Deviate only with an ADR that names this
  trade-off. Source: Evans, "Core Domain": "Make the core small".
- [invariant] Event sourcing, CQRS with a separate read store, and a message broker enter the code only with an
  accepted ADR naming the problem, the need, the trade-off and the exit. Why: "for most systems CQRS adds risky
  complexity", event sourcing is "very hard to retrofit", a broker adds a failure domain. Test: a change adding a
  broker client, an event-store package or table, or a second read model without a linked accepted ADR is
  rejected in review. Source: https://martinfowler.com/bliki/CQRS.html,
  https://martinfowler.com/eaaDev/EventSourcing.html.

### Language

- [invariant] One term per concept inside a context, the same in code, UI, API fields, docs and tickets.
  `docs/GLOSSARY.md` (`term | aliases | meaning in this project | not to confuse with | source`, kept with the
  `glossary` skill) is the record; a term with two meanings gets one row per context. A rename edits the glossary
  row first, then code, UI and docs in the same change. Why: "a change in the language is a change to the model".
  Test: a whole-word search for each alias over code identifiers (locale files excluded) hits only the glossary
  and anti-corruption layers; a new domain class or event without a row fails review. Source: Evans, "Ubiquitous
  Language".

### Contexts and dependencies

- [invariant] Each bounded context is one module with a declared public surface (application services or a query
  interface, published events, shared value types), and an arch test in CI keeps everyone else on it: Pest
  `toOnlyBeUsedIn` and `not->toUse`, Go `internal/` plus a `go list` edge check, dependency-cruiser or
  eslint-plugin-boundaries. Why: Evans asks to set boundaries in "code bases and database schemas"; a boundary in
  a diagram is crossed by the first deadline. Test: plant an import of another context's interior; the test fails.
  Source: Evans, "Bounded Context"; https://pestphp.com/docs/arch-testing; https://pkg.go.dev/cmd/go;
  https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md.
- [invariant] Dependencies between contexts point one way with no cycle. `docs/CONTEXT-MAP.md` has one row per
  pair: upstream, downstream, relationship (partnership, shared kernel, customer/supplier, conformist,
  anti-corruption layer, open host service, separate ways), mechanism and enforcing rule; the arch test's allowed
  edges are the same set. Why: an edge missing from the map is a contract nobody reviewed. Test: diffing map rows
  against allowed edges shows nothing; a planted context cycle fails. Source: Evans, "Context Map";
  https://martinfowler.com/bliki/BoundedContext.html.
- [invariant] A context owns its tables. Others never read, join or write them; they call the owner's query
  interface, keep a copy fed by its events, or read a view it publishes and versions. Why: a direct read makes the
  schema an unversioned contract and skips the owner's rules. Test: a table-to-context map plus a scan fails when
  another context's model, query builder or SQL names the table. Source: "each service owns a set of tables that
  must only be accessed by that service" (https://microservices.io/patterns/data/database-per-service.html).
- [default] A shared kernel is small, named and changed only with review from every context that shares it. No
  catch-all `Common`, `Shared` or `Utils` module; technical helpers (money, clock, IDs) import no context.
  Trade-off: small types get duplicated. Deviate only with an ADR that names this trade-off. Proof: an arch test
  that kernel and helpers use no context namespace. Source: Evans, "Shared Kernel": "Keep this kernel small".
- [default] Vendors and legacy systems sit behind an anti-corruption layer in the downstream context that
  translates both ways; vendor types never reach the domain. Build it as the `build-vs-buy` adapter.
  Trade-off: a layer to follow every upstream change; conformist is cheaper when the upstream model fits. Deviate
  only with an ADR that names this trade-off. Proof: the SDK namespace is used only inside the layer. Source:
  Evans, "Anticorruption Layer", "Conformist".

### Aggregates

- [invariant] An aggregate is the boundary of one set of invariants. One transaction changes one aggregate; others
  are referenced by ID, outsiders hold the root only, and cross-aggregate rules settle after commit via events.
  Why: "Transactions should not cross aggregate boundaries". Test: a structural test fails when a root has a
  property typed as another root; a use case saving two aggregates in one transaction fails review unless it names
  the invariant (then merge them). Source: https://martinfowler.com/bliki/DDD_Aggregate.html; Vernon, "Reference
  Other Aggregates By Identity" (https://www.dddcommunity.org/library/vernon_2011/).
- [invariant] Invariants are enforced and tested at the root: a method refuses an invalid transition with a named
  domain error, and the unit test calls the root without HTTP, queue or database. Controllers, jobs and services
  load, call, save and publish; they hold no rule. Why: the next entry point skips a rule kept in a controller.
  Test: one root-level unit test per listed invariant (confirm after the hold expired raises `HoldExpired`); no
  status check of that aggregate in controllers or jobs. Source: https://martinfowler.com/bliki/AnemicDomainModel.html.
- [default] Keep aggregates small; growing collections (a room's bookings, a customer's invoices) are separate
  aggregates. Trade-off: more eventual consistency and events. Deviate only with an ADR that names this
  trade-off. Source: Vernon, "Design Small Aggregates" (URL above).

### Messages

- [invariant] Each message has one kind, named for it: a command asks one handler to act and may be refused
  (`ConfirmBooking`); a domain event is a past-tense fact inside one context (`BookingConfirmed`); an integration
  event is a versioned, published contract with an owner in the map (`cross-service-contracts`). Names like
  `{Aggregate}Updated`, `Changed`, `Saved` or `Modified` are refused. Why: an event that hides a request obscures
  intent, and a generic name makes every consumer diff the payload. Test: a naming check fails on those suffixes
  and imperative event names; each integration event has a typed, versioned schema. Source:
  https://martinfowler.com/articles/201701-event-driven.html,
  https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation.
- [invariant] Events are recorded in the transaction that changed the aggregate and published after commit or
  through an outbox; consumers are idempotent by event ID (`async-reliability`). Why: integration events "should
  occur only if the entity is successfully persisted". Test: roll back the change, nothing is published; deliver
  an event twice, one effect. Source: Microsoft URL above; https://microservices.io/patterns/data/transactional-outbox.html.
- [invariant] An event is not a remote procedure call. A sender that needs the work done or its outcome calls the
  owner's public surface or sends a command and handles refusal; it never waits for or reads a consumer's
  reaction. Why: the flow turns invisible and breaks when a consumer is slow. Test: no producer path reads state
  written by a consumer of its own event. Source: Fowler, event-driven article above.
- [invariant] Decisions stay with their owner: the owner puts them in the event as facts (`refundDue`,
  `amountDue`), and consumers act without recomputing the rule. Why: a re-derived rule drifts at its first change
  and two contexts disagree about one booking. Test: consumer tests use producer golden fixtures; an arch test
  keeps the owner's policy classes inside the owner. Source: reproducible with the test above.

### Long flows

- [default] A flow across contexts with more than two steps, a compensation or a deadline runs in a process
  manager with stored state per instance; one reaction to one event stays choreography. Trade-off: a central
  component that knows every participant, versus a flow "not explicit in any program text". Deviate only with an
  ADR that names this trade-off. Source: https://microservices.io/patterns/data/saga.html,
  https://www.enterpriseintegrationpatterns.com/patterns/messaging/ProcessManager.html.
- [invariant] Every step has a deadline with a defined outcome, every step a later failure invalidates has a
  compensating action, and flow state survives a restart. Why: a saga has no "automatic rollback". Test: advance
  the clock past each deadline, the flow times out and each compensation runs once; kill between two steps,
  restart, the flow resumes. Source: microservices.io saga (URL above).

## Procedure

### Fast path

1. Read `docs/GLOSSARY.md`, `docs/CONTEXT-MAP.md` and the arch test. Missing: say so; never invent contexts.
2. Store, list and show only: a plain CRUD module in the owning context. Go to step 6.
3. Cross-context call or read: the pair is in the map and uses the owner's public surface, never its tables.
4. New event: glossary term, past tense, not `{Aggregate}Updated`; an integration event is a contract.
5. Publish after commit or through the outbox; the consumer is idempotent (`async-reliability`).
6. Run the arch test (`vendor/bin/pest tests/Arch`, `go test -count=1 ./archtest/...`,
   `npx dependency-cruiser src` or `npx eslint .`) and report the result.
7. Ask the owner before a new context, a new integration event contract, a service split, event sourcing, CQRS
   or a broker.

### Full procedure

1. Classify the change: module, aggregate, event, cross-context call, long flow, vendor or legacy integration.
2. Decide the depth ([references/when-ddd-pays.md](references/when-ddd-pays.md)); event sourcing, CQRS or a
   broker gets the ADR first.
3. Look up the terms in the glossary; propose rows for new terms to the owner. A rename edits the row first.
4. Place the code in one context; a new edge updates the map and the arch rule in the same change.
5. Aggregate: invariants on the root, one unit test each. Message: kind, name, publication, idempotent consumer.
   Long flow: orchestration or choreography, deadlines, compensations, stored state.
6. Plant one violation per new arch rule, watch it fail, revert, run the suite. Report what ran.

## Traps

- Anemic domain: entities with getters and setters, rules in controllers and jobs. Next month's API endpoint
  skips them.
- A `Common` or `Shared` module everyone imports: one change there touches every context.
- Events as remote calls: an `InvoiceRequested` event whose producer then waits for `InvoiceCreated`.
- One huge aggregate (`Customer` with every booking and invoice) locks on every write and loads every collection.
- `BookingUpdated` with the whole row: each consumer diffs fields to guess what happened.
- Arch tools that fail open: dependency-cruiser rules default to `warn`, eslint-plugin-boundaries with
  `default: "allow"`, a cached `go test` run, a rule on a misspelt namespace. See
  [references/arch-tests.md](references/arch-tests.md).
- DDD vocabulary on a settings form: repositories, factories and value objects for data in, data out.

## Done when

- New terms have glossary rows; a rename reached code, UI and docs in one change.
- The map lists every edge, the arch test enforces each one, and each new rule was seen failing once.
- Aggregates have their invariants on the root with a unit test each; each use case writes one aggregate.
- Events have specific past-tense names, are published after commit or through the outbox, and have idempotent
  consumers; integration events have a versioned contract. Long flows have deadline and compensation tests.
- Event sourcing, CQRS, a broker, a new context, a new contract or a service split has an ADR or the owner's
  recorded decision.

## References

- [references/when-ddd-pays.md](references/when-ddd-pays.md): load when choosing CRUD or a modelled context, or
  when someone proposes event sourcing, CQRS or a broker.
- [references/contexts-and-map.md](references/contexts-and-map.md): load when adding a context or an edge,
  writing the context map, choosing a relationship type or building an anti-corruption layer.
- [references/arch-tests.md](references/arch-tests.md): load when writing or extending the boundary test in PHP,
  Go or TypeScript.
- [references/aggregates.md](references/aggregates.md): load when designing an aggregate or testing invariants.
- [references/events-and-flows.md](references/events-and-flows.md): load when adding a command, event, consumer
  or cross-context flow.

## Sources

All verified 2026-11-04.

- https://www.domainlanguage.com/ddd/reference/ (Evans, DDD Reference, CC BY 4.0): contexts, language,
  aggregates, events, context map patterns, core domain.
- https://martinfowler.com/bliki/BoundedContext.html, https://martinfowler.com/bliki/DDD_Aggregate.html,
  https://martinfowler.com/bliki/AnemicDomainModel.html, https://martinfowler.com/bliki/CQRS.html,
  https://martinfowler.com/articles/201701-event-driven.html, https://martinfowler.com/eaaDev/EventSourcing.html.
- https://www.dddcommunity.org/library/vernon_2011/ (Vernon, "Effective Aggregate Design", parts I and II).
- https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation.
- https://microservices.io/patterns/data/saga.html, https://microservices.io/patterns/data/transactional-outbox.html,
  https://microservices.io/patterns/data/database-per-service.html,
  https://www.enterpriseintegrationpatterns.com/patterns/messaging/ProcessManager.html.
- https://pestphp.com/docs/arch-testing, https://github.com/sverweij/dependency-cruiser,
  https://github.com/javierbrea/eslint-plugin-boundaries (via Context7), https://pkg.go.dev/cmd/go; Pest 4.7.8,
  dependency-cruiser 18.7.2 and go1.27.3 configs run against planted violations.
