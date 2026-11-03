---
name: plan-entitlements
description: "Designs plan limits and features for B2B SaaS: one typed entitlement schema, one resolver (plan, custom plan, override with reason and expiry, add-ons), race-free quota checks, soft and hard limits, downgrades that keep data, per-cycle resets, usage in the UI. Use when adding a limit, feature gate, add-on, enterprise override or downgrade rule. Not for prices, VAT or invoices (billing-eu-b2b)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Plan entitlements

This skill decides what a tenant may use: which limits and features exist, how a plan, a custom contract, an
override and purchased add-ons combine into one answer, where that answer is enforced, and what happens to
existing data when the answer shrinks. Money, tax, proration and payment webhooks belong to `billing-eu-b2b`;
choosing price points and plan packaging to `pricing-and-unit-economics`; the tenant tree to `tenancy-model`. The
failure it prevents: limits checked in five places with five different answers, so a customer either gets more
than they paid for or loses data they paid to keep.

## Applies when / does not apply

- Applies: adding a numeric limit, a boolean feature or an enumerated option to plans; a custom or enterprise
  plan; a per-tenant override promised by sales or support; add-ons and purchased packs; quota checks on create,
  invite, publish or resume; downgrade, cancellation and suspension effects; per-cycle allowances and resets;
  usage and limit displays; admin tools that edit any of these.
- Does not apply: prices, VAT, invoices, proration amounts and payment-provider webhooks (`billing-eu-b2b`), price
  points and packaging (`pricing-and-unit-economics`), percentage rollouts and experiment flags (a feature-flag
  system), login rate limits and abuse throttles unrelated to a plan, role permissions (`authorization-rbac`).

## Rules

Most important first. Examples use an invoicing app: plans limit seats, customers and invoices per month, gate
API access, and offer a choice of e-invoice formats; reminder SMS are sold as credits.

- [invariant] One typed entitlement schema declares every key once: kind (count limit, value limit, boolean
  feature, enum or set), unit, how "unlimited" is written, what 0 means, a floor where the rest of the system
  needs one, the usage function for count limits, hard or soft, and the downgrade behaviour. Plans, custom plans,
  overrides and admin editors are validated against it, and unknown keys are rejected when written. Why: a key
  missing from the schema cannot be overridden and silently keeps its inherited value, and a lookup that
  defaults to 0 turns a typo into "blocked" or into a limit that never binds. Test: a completeness test that
  every plan defines or inherits every key and every count limit has a usage function; writing an override with
  an unknown key fails validation. Source: reproducible with the test above.
- [invariant] Unlimited is an explicit value (null or a typed marker), never 0 or a negative sentinel, and 0
  always means "none". Why: when 0 means "unlimited" for one key and "keep nothing" for a retention key, a
  bulk edit that zeroes keys deletes data or lifts caps. Test: per key, 0 blocks the first unit and unlimited
  allows usage far above any plan value. Source: reproducible with the test above.
- [invariant] One resolver computes the effective entitlements, and every check goes through it: web, API,
  imports, sync jobs, automation and agent tools, background jobs, admin impersonation. Order: base plan (a custom
  plan replaces the standard plan, it does not stack) → per-tenant overrides replace the value of the keys they
  name → add-ons add purchased quantity on top → restrictions (suspension, abuse hold, unpaid) cap last. Why: a
  check outside the resolver forgets overrides or add-ons, and the customer sees one number and hits another.
  Test: an architecture test that only the resolver reads plan definitions and override rows; per channel, a
  create at the limit is refused with the same error. Source: reproducible with the test above.
- [invariant] Code checks entitlements, never plan identity: no `plan == 'pro'`, no per-plan maps keyed by plan
  name with a default for the rest. Why: a custom plan with the same entitlements as a standard plan falls into
  the default branch and silently loses features. Test: a custom plan copied from a standard plan behaves the
  same in every boundary test; a CI grep fails on comparisons with plan names outside the plan catalog. Source:
  reproducible with the test above.
- [invariant] Overrides are records, not edits: tenant, key, value, reason, author, start, expiry (or an explicit
  "permanent" with a reason), and a contract or ticket reference. Expiry is evaluated when the resolver reads,
  not by a cleanup job, and cached entitlements expire no later than the earliest override expiry. Creating,
  changing and removing an override is audited. Why: an override without expiry outlives the deal, and one that
  depends on a nightly job stays active when the job fails. Test: an override that expired yesterday does not
  apply with no job run; an override without a reason is rejected; each change writes one audit row with before
  and after. Source: reproducible with the test above.
- [invariant] Restrictions apply after overrides and add-ons and are never lifted by them. The resolved result
  carries the restriction and its reason, and the UI and error messages read that marker instead of recomputing
  the rule. Why: a generous override must not reopen a suspended or unpaid tenant. Test: a suspended tenant with
  an override of 1,000 customers resolves to the restricted value and the error names the suspension. Source:
  reproducible with the test above.
- [invariant] Quota checks run on the server and are serialized with the write: lock the tenant row or take a
  transaction-level advisory lock before count and insert, or use an atomic conditional update for counters and
  balances. The losing request gets a domain error that names the key, limit and usage, never a 500. The SQL
  recipe lives in `billing-eu-b2b`. Why: check-then-insert lets parallel requests pass the same last slot. Test:
  N parallel creates at limit minus one on PostgreSQL give exactly one success. Source: CWE-367, "The product
  checks the state of a resource before using that resource, but the resource's state can change between the
  check and the use" (https://cwe.mitre.org/data/definitions/367.html, verified 2026-11-03); PostgreSQL docs,
  `FOR UPDATE` "prevents them from being locked, modified or deleted by other transactions until the current
  transaction ends" (https://www.postgresql.org/docs/current/explicit-locking.html, verified 2026-11-03).
- [invariant] Usage is counted for the tenant, never through a viewer's scope, by one usage function per count
  key, and the enforcer, the downgrade handler, the reactivation path and the UI all call it. The function states
  what counts (active or paused, published or draft, owner excluded from seats). Why: a count through a viewer's
  visibility scope reports 1 of 20 to a member who sees one record and lets them create past the limit; a count
  key without a usage function reads 0 and never binds. Test: a member who sees one of 20 customers cannot create
  the 21st on a 20-customer plan; usage, enforcement and display agree on a fixture with paused and draft rows.
  Source: reproducible with the test above.
- [invariant] Add-ons cannot open what the plan closes: an add-on raises a key only where the base allows it (count
  above 0, feature on). On downgrade, booked add-on quantities are clamped to what the new plan permits;
  reductions bought by the customer take effect at period end. Why: a cheap add-on on a plan that excludes the
  resource is a backdoor to a higher plan, and a downgrade that keeps old add-ons keeps the old plan's features.
  Test: buying a seat add-on on a plan with 0 extra seats is refused; after a downgrade the resolver shows the
  clamped quantity. Source: reproducible with the test above.
- [invariant] A downgrade or suspension never deletes. Each key's downgrade behaviour is one of: block new (count
  over limit, nothing removed), pause excess (newest first, with a reason, restored on upgrade with the same IDs),
  or lossy (shorter retention, coarser intervals, fewer regions). Lossy changes get a preview with concrete
  numbers before confirmation, a notice to the owner, and a grace period before anything is removed; retention
  never drops below a floor. Suspension uses only reversible behaviours. Why: what was deleted cannot be sold back
  on upgrade. Test: downgrade then upgrade restores every paused record with the same ID; during the grace period
  data older than the new retention window is still there. Source: reproducible with the test above.
- [invariant] Included allowances and purchased packs are separate balances: the included allowance resets per
  billing cycle, packs persist until used or until their stated expiry. Consumption takes the included allowance
  first, then packs. Debits are atomic conditional updates, and the reset is keyed by (tenant, period) so running
  it twice resets once. Why: one shared balance lets a reset wipe what the customer paid for. Test: reset the same
  period twice (one reset); a reset leaves the pack balance unchanged; parallel debits never drive a balance
  below zero. Source: reproducible with the test above.
- [invariant] Feature checks fail closed: an unknown key or a tenant without a resolvable subscription resolves to
  the baseline plan, never to "no limits". In tests an unknown key throws. Why: a missing subscription row after
  a failed checkout should not unlock everything. Test: a tenant with no subscription gets baseline values;
  checking an undeclared key in the test environment raises. Source: reproducible with the test above.
- [invariant] Cached entitlements are invalidated on every input change: plan edits (every tenant on that plan),
  override writes, add-on changes, subscription state changes and restriction changes. The cache key carries a
  version of the cached shape, so two releases never read each other's entries. Why: a five-minute stale cache
  after an upgrade is a support ticket; a stale cache after a suspension is free service. Test: change an
  override and read in the same request cycle; the new value applies without waiting for a TTL. Source:
  reproducible with the test above.
- [invariant] Every key has boundary tests generated from the schema: limit minus one allowed, at limit refused
  (hard) or degraded (soft), 0, unlimited, override raising and expiring, add-on, downgrade behaviour. Why: a key
  added without tests is the one that never binds. Test: adding a key to the schema without its matrix entry
  fails the suite. Source: reproducible with the test above.
- [default] Each limit is declared hard or soft. Hard limits refuse with a 4xx that names key, limit, usage and
  the upgrade path. Soft limits keep working and degrade in a stated way (for example, only the first N
  recipients are notified) with warnings at set thresholds. Trade-off: soft limits need a defined degradation and
  monitoring of who sits above them. Deviate only with an ADR that names this trade-off. Proof: a test per soft
  key that shows the degradation, not a refusal.
- [default] The UI shows usage and limits from the same resolver and usage function, through one endpoint or
  page prop, and the client never computes limits from plan data. Hiding a button is a hint, not enforcement.
  Trade-off: one more request or prop, in exchange for the screen and the error agreeing. Deviate only with an ADR
  that names this trade-off. Proof: a test that the display payload and the refusal error report the same numbers.
- [default] Abuse throttles and creation-rate budgets are a separate key class: add-ons and overrides for sold
  limits do not raise them, and a refusal says it is a rate limit, not a plan limit. Trade-off: a second set of
  keys to tune. Deviate only with an ADR that names this trade-off. Source: OWASP API Security Top 10 2023, API4:
  "Limit/throttle how many times or how often a single API client/user can execute a single operation"
  (https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption, verified 2026-11-03).
- [default] Upgrades take effect at once; downgrades take effect at period end. Free-tier allowances that should
  not multiply with organization count are counted per owner, not per tenant (see `tenancy-model` for owner
  changes). Trade-off: per-owner counting needs recomputation on ownership transfer and deletion. Deviate only
  with an ADR that names this trade-off. Proof: a second free organization of the same owner resolves to the
  restricted allowance.
- [default] When a payment provider manages entitlements, mirror them locally and keep the resolver as the only
  reader; reconcile from the provider's list endpoint after missed webhooks. Trade-off: a local copy to keep in
  sync. Deviate only with an ADR that names this trade-off. Source: Stripe docs, "We recommend you persist these
  entitlements internally for faster resolution." (https://docs.stripe.com/billing/entitlements, verified
  2026-11-03).

## Procedure

1. Gate: does the change add or alter what a tenant may use, or how much? If it only changes a price or an
   invoice, use `billing-eu-b2b`.
2. Declare the key in the schema with kind, unit, zero and unlimited meaning, floor, usage function, hard or soft,
   and downgrade behaviour.
3. Set values for every standard plan; custom plans inherit unless they set the key.
4. Enforce through the resolver at every entry point (web, API, jobs, imports, tools), serialized with the write.
5. Add the key's downgrade handling and its reactivation path.
6. Expose usage and limit to the UI through the same resolver.
7. Generate the boundary tests and run the parallel-create test on PostgreSQL.
8. If sales asked for an exception: create an override record with reason, author and expiry, not a plan edit.

## Traps

- A plan editor built from a hand-written list of keys drifts from the plan definitions; a key missing from the
  list cannot be overridden and nobody notices.
- A per-plan map that defaults unlisted plans to 0 also catches every custom and enterprise plan.
- Counting usage through the viewer's visibility scope underreports for restricted members.
- Draft or paused rows that do not count toward a limit pile up without end unless a total ceiling exists.
- An override that sets an absolute value can swallow purchased add-ons if add-ons are applied before it.
- A downgrade that clamps a value limit (retention, interval, regions) is lossy even though it "only changes a
  setting".
- Running the lossy add-on clamp on suspension makes a temporary payment problem permanent.
- A cached resolved object whose class gained a field cannot be read by the other release during a rolling
  deploy; version the key.

## Done when

- The schema declares every key with its semantics, and the completeness test is green.
- Every check goes through the resolver; the architecture test and the plan-name grep are green.
- Overrides carry reason, author and expiry, are audited, and expire without a job.
- Each count key has one usage function shared by enforcement, downgrade, reactivation and UI.
- Downgrade then upgrade restores paused records with the same IDs; lossy keys have preview, notice and grace.
- The boundary matrix and the parallel-create test pass on PostgreSQL.

## References

- [references/schema-and-resolver.md](references/schema-and-resolver.md): load when declaring keys, writing the
  resolver, storing overrides or building the admin editor.
- [references/downgrade-and-metering.md](references/downgrade-and-metering.md): load when handling downgrade,
  cancellation or suspension, add-on clamping, per-cycle resets or purchased packs.
- [references/test-matrix.md](references/test-matrix.md): load when writing the boundary tests for a key.

## Sources

- https://cwe.mitre.org/data/definitions/367.html: time-of-check time-of-use race, verified 2026-11-03.
- https://www.postgresql.org/docs/current/explicit-locking.html: row-level `FOR UPDATE` locks held until the
  transaction ends, verified 2026-11-03.
- https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption: throttling single
  operations, spending limits, verified 2026-11-03.
- https://docs.stripe.com/billing/entitlements: provider-managed entitlements, local persistence, changes apply
  to existing subscriptions at the next billing period, verified 2026-11-03.
