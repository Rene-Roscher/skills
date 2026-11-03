---
name: billing-eu-b2b
description: "Engineers subscription billing for EU and German B2B SaaS with the provider behind an adapter: integer money, reverse charge with proof, idempotent webhooks, proration, dunning, race-free limits, EN 16931 e-invoices. Use when touching checkout, subscriptions, invoices, payment webhooks (Mollie, Stripe), VAT IDs, prices or coupons, even small changes. Not for plan limits and overrides (plan-entitlements), pricing copy or tax advice."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# EU B2B billing

This skill sets the rules for subscription billing in an EU or German B2B SaaS that keeps plans, limits, tax
and invoices in its own code and reaches the payment service provider (PSP) through an adapter. PSP syntax
stays in the provider's docs, and the adapter design is in `build-vs-buy`. It prevents money state that is off
by a cent, charged twice, charged without a record, or taxed wrongly. Tax and invoice content is a
review-ready draft for the DE/EU scope, not legal or tax advice; statute and standard quotes were checked
against the primary sources on 2026-10-31.

## Applies when / does not apply

- Applies: checkout, subscriptions, renewals, proration, add-ons, coupons, price locks, dunning, PSP webhooks,
  VAT IDs and tax rates, invoices and credit notes, e-invoices, plan limits, quotas and usage credits. Small
  requests in these areas count, such as adding a coupon or explaining a one-cent difference.
- Does not apply: pricing-page design or copy, formatting amounts for display, PSP SDK syntax (provider docs),
  bookkeeping in the accounting system, sales to consumers (destination VAT and consumer-law duties are not
  covered), and legal or tax advice.

## Rules

### Money and tax

- [invariant] Store and compute money in integer minor units or an exact decimal or money type, and name the
  rounding mode wherever rounding happens. Never multiply binary floats and call `round()`. Why:
  `(int) round(250 / 100 * 1.19 * 100)` is 298 on PHP 8.3.10 and 297 on PHP 8.4.27, because the float is
  297.49999999999994 and PHP 8.4 removed `round()`'s pre-rounding; the exact value 297.5 rounds half up to 298.
  Test: a guard fails the build on float casts, `round`, `floor`, `ceil` or `/` on amounts in the billing code
  outside one allowlisted money helper; a property test checks that helper over a cent range for every
  configured rate; the suite aborts on a runtime minor version other than production's. Source:
  https://github.com/php/php-src/blob/PHP-8.4/UPGRADING (verified 2026-10), reproduced on both versions
  2026-10-31.
- [invariant] One tax computation serves checkout, renewal, proration and invoice rendering, and the amount
  charged equals the invoice total with VAT (BT-112). Why: EN 16931 computes VAT per VAT category on the summed
  taxable amount, so a charge built from per-line gross amounts can differ from the invoice by a cent. Test:
  for a set of mixed baskets, the charged amount equals BT-112 exactly. Source: EN 16931 rules BR-CO-14,
  BR-CO-15, BR-CO-17, https://github.com/ConnectingEurope/eInvoicing-EN16931 (verified 2026-10).
- [default] The net price is the stored source of truth; gross and tax are derived from it per customer.
  Trade-off: every screen or export that shows a gross amount needs the tax resolver. Deviate only with an ADR
  that names this trade-off. Source: BR-CO-17 computes tax from the taxable (net) amount.
- [invariant] The tax rate and treatment are explicit inputs from one resolver and are stored on each invoice.
  Never read them from ambient state (current tenant, request, locale), and never derive them again later from
  today's customer data. Why: renewal jobs run without a request or tenant context, so an ambient lookup there
  finds no tenant and falls back to domestic VAT for reverse-charge customers; an invoice must not change when
  the customer edits a VAT ID next month. Test: a table-driven resolver test (seller country, buyer country, business confirmed, VAT ID
  status) returns treatment and rate; a renewal-job test for an EU reverse-charge customer asserts a net-only
  charge; the invoice row stores treatment, rate and both VAT IDs. Source: VAT Directive 2006/112/EC Art. 44
  and Art. 196, UStG § 3a Abs. 2 (verified 2026-10), see the VAT reference.
- [invariant] Grant reverse charge only on positive confirmation: the VAT ID format is valid, the EU VIES
  registry answers `valid: true`, and where it returns a trader name, the name matches the customer. Unknown,
  timeout and "unavailable" never count as confirmed. Store the proof: returned name, match result, request
  identifier, timestamp. Why: VAT IDs are printed in every imprint, so "valid" alone proves nothing about the
  buyer, and wrongly granted reverse charge leaves the seller owing the VAT. Test: cases for valid, invalid,
  unavailable, name mismatch and name not published; only a confirmed case grants reverse charge. Source:
  https://ec.europa.eu/assets/taxud/vow-information/swagger_publicVAT.yaml (verified 2026-10). What to charge
  while a number is unconfirmed is a tax decision; record it in the project profile.
- [invariant] Fixtures for the VAT registry and the PSP come from recorded real responses and carry their
  source and recording date. Why: a fake that returns a remembered field name agrees with the bug, so the suite
  stays green while production misreads every answer. Test: a test fails on any fixture without the source and
  date header. Source: reproducible by the test; general rule in `build-vs-buy`.
- [invariant] A reverse-charge invoice carries the reverse-charge wording, both VAT IDs, VAT category AE with
  rate 0 and tax amount 0, and an exemption reason; for services under UStG § 3a Abs. 2 it is issued by the 15th
  day of the month after the supply. Test: rendering test for treatment `reverse_charge` asserts the wording
  "Steuerschuldnerschaft des Leistungsempfängers" (or "Reverse charge"), seller and buyer VAT IDs, category AE,
  rate 0, category tax 0 and reason. Source: https://www.gesetze-im-internet.de/ustg_1980/__14a.html, EN 16931
  BR-AE-02, BR-AE-05, BR-AE-09, BR-AE-10 (verified 2026-10).
- [invariant] If the offer is B2B only, the server enforces it: signup stores a business confirmation, and the
  backend rejects signups without it. Why: the tax and invoice rules here assume every buyer is a business, and
  a form-only check lets consumers through, which brings destination VAT and consumer-law duties this skill does
  not cover. Test: a request test posts a signup without the confirmation and gets a validation error from the
  backend, not only from the form. Source: reproducible with the test above.

### Payment provider webhooks

- [invariant] A webhook body moves no money state on its own. Verify the signature where the PSP signs, with
  the library's timestamp tolerance (never 0). Where the PSP sends only an ID, fetch the object from the PSP API
  with your own credentials and act on that. Unknown or deleted IDs get a 2xx with no side effect. Why: bodies
  can be forged or stale, and a non-2xx for unknown IDs tells a prober which IDs exist and triggers retries.
  Test: forged body with an unknown ID returns 2xx and changes nothing; a signature outside the tolerance is
  rejected; a refund delivered before "paid" still ends in the correct state. Source:
  https://docs.mollie.com/reference/webhooks, https://docs.stripe.com/webhooks (verified 2026-10).
- [invariant] Acknowledge with 2xx only after the event is processed or durably stored for processing. A
  transient failure returns non-2xx so the PSP retries, or lands in your own inbox with retries. Why: retry
  windows end (one PSP retries 10 times over about 26 hours, another up to three days in live mode), and an
  acknowledged event that was neither processed nor stored is lost. Test: a PSP fetch timeout yields non-2xx
  or an inbox row, never a bare 2xx. Source: the Mollie and Stripe webhook docs above.
- [default] Use an inbox: persist the raw event, acknowledge at once, then process asynchronously and
  idempotently. Before acting, fetch the current state from the PSP, also for PSPs that sign full payloads,
  because delivery order is not guaranteed. Trade-off: a table, a worker, an API call per event and a
  retention period for raw events. Deviate only with an ADR that names this trade-off. Source:
  https://docs.stripe.com/webhooks (order not guaranteed, verified 2026-10).
- [invariant] Claim each webhook effect exactly once with insert-on-conflict on a unique key that includes the
  state transition you act on, such as (provider, payment ID, transition). Never check `exists()` and then
  insert. Why: two deliveries both see "not exists", the second insert hits the unique index and returns 500;
  on PostgreSQL a caught unique violation aborts the surrounding transaction; a key without the transition
  swallows a chargeback that reuses the paid payment's ID. Test: two parallel deliveries produce one effect on
  a PostgreSQL test database; paid, refunded and charged back on one ID produce three effects. Source:
  https://www.postgresql.org/docs/current/sql-insert.html (ON CONFLICT DO NOTHING, verified 2026-10).
- [invariant] Compare the settled amount and currency with the local record before marking anything paid. A
  mismatch changes no state and alerts a human. Test: a PSP fixture one cent off leaves the transaction pending
  and emits an alert.

### Charges and subscriptions

- [invariant] Record, then charge. Persist a pending transaction with a deterministic unique idempotency key,
  commit, then call the PSP outside any database transaction with the same key. The webhook falls back to that
  key (passed as PSP metadata) when the external ID was never stored, and a reconcile sweep resolves stuck
  pending rows. Why: a charge inside a database transaction can succeed at the PSP while the database rolls
  back, which takes money without a record, and it holds a pooled connection during an HTTP call. Test: the
  charge runs outside any open transaction; a PSP exception leaves a pending row; two concurrent attempts
  produce one charge; the reconcile command resolves pending rows with and without an external ID.
- [invariant] Your own unique key in your own database is the durable idempotency guard. PSP idempotency keys
  are a short-lived second layer, and SDK idempotency state is reset per call in long-lived workers. Why: one
  PSP removes keys older than one hour and another may prune them after 24 hours; a singleton SDK client kept a
  failed charge's key, and the next customer's charge replayed it. Test: with mocked HTTP, a failed charge
  followed by a charge for another customer sends a different key. Source:
  https://docs.mollie.com/reference/api-idempotency, https://docs.stripe.com/api/idempotent_requests
  (verified 2026-10).
- [invariant] Claim each renewal per period with a unique key such as (subscription, period end). Create the
  transaction, apply credits and advance the period in one database transaction, and charge outside it. Do not
  retry a charge job automatically after the period has advanced. Why: a retried renewal job read the advanced
  period, built a new claim key and charged the next period. Test: two stale renewal runs produce one charge
  and one period advance; the charge job is configured with a single try.
- [invariant] Encode billing invariants as database constraints and fail loudly on impossible states. A move
  from free to paid goes through the full first-charge path, never through proration, and tests assert the
  charge and the period, not only the plan name. Why: an upgrade prorated against a free subscription without
  a period end computed 0, created no transaction, and left a paid plan that never came due. Test: a CHECK
  constraint such as `plan = 'free' OR status <> 'active' OR current_period_end IS NOT NULL` rejects the bad
  write on PostgreSQL; proration throws on a missing period; the free-to-paid test asserts a transaction for
  the full first period and a period end.
- [invariant] Proration and add-ons use one pro-rata function in integer minor units, with a documented time
  basis (seconds or days) and explicit rounding. Period switches include add-ons, an unused remainder becomes a
  credit, and prorated parts never add up to more than the full price. Test: table tests for a mid-period
  upgrade, monthly to annual with add-ons, an add-on bought on the last day, a downgrade credit and a leap-year
  February, plus a property test that the parts never exceed the whole.
- [invariant] Model only states the code writes. Find the real entry state (often a free plan or a
  complimentary period) instead of assuming a trial, and remove enum cases, KPIs and badges for states nobody
  writes. Why: a revenue tile for a status no code ever wrote showed 0 forever and looked healthy. Test: a
  static scan finds a writer for every subscription status case, and every KPI query has a seeded fixture that
  returns more than 0.
- [default] Dunning is an explicit state machine: bounded retries on a schedule, a payment-method validity
  check before each retry (an invalid mandate or expired card stops retries and asks for a new method),
  customer notices, a grace period and a reversible suspension. Suspension never shortens data retention while
  the account can still recover. Trade-off: more states to build, test and support. Deviate only with an ADR
  that names this trade-off. Proof: one test per transition, and a retention test for a suspended account.

### Limits, prices and discounts

- [invariant] Serialize plan-limit checks with the insert: lock the tenant row (`SELECT ... FOR UPDATE`) or
  take a transaction-level advisory lock keyed by tenant and limit before count and insert. Counters and credit
  balances use an atomic conditional update (`UPDATE ... SET balance = balance - n WHERE balance >= n`). Limits
  are enforced on the server; the UI only shows hints. Why: check-then-insert lets double clicks and API
  scripts exceed a sold limit. Test: N parallel creates at limit minus one, on PostgreSQL, give exactly one
  success and clean domain errors for the rest, not a 500. Source:
  https://www.postgresql.org/docs/current/functions-admin.html (`pg_advisory_xact_lock`, verified 2026-10).
- [default] One plan resolver and one limit service own all limit semantics (can, limit, usage, remaining).
  Downgrades pause or deactivate the newest excess with a reason and reactivate it on upgrade; they never
  delete. Abuse caps and creation-rate budgets stay separate from sold limits. Trade-off: one more indirection
  for every limit check. Deviate only with an ADR that names this trade-off. Proof: an architecture test that
  only the limit service reads limit config, and a downgrade-upgrade round trip that restores every record with
  the same IDs.
- [default] Prices, plan, quantity and currency come from the server-side catalogue, never from the client.
  Price locks are stored per subscription at purchase, not toggled globally. Admin plan changes start from the
  current plan and show immediate charges and downgrade effects before confirming. Trade-off: a snapshot per
  subscription and an extra confirmation step for staff. Deviate only with an ADR that names this trade-off.
  Proof: a request test with a tampered price or plan is ignored, and a locked price survives a catalogue
  change.
- [invariant] Discounts reduce the net amount before VAT and stay strictly below the net price; computed
  discounts are capped. A new discount kind means auditing every path that assumed the old kinds. Why: a guard
  written for percentages skipped fixed-amount coupons silently, and a discount equal to the price leads into
  the zero-amount path that other code treats as a free plan. Test: one test per discount kind across checkout,
  renewal, proration, preview and invoice, and a CHECK constraint on coupon kind and value.

### Invoices

- [invariant] An EN 16931 e-invoice never carries a negative item net price. Express credits and discounts as
  document-level allowances (BG-20), whose amounts sum to BT-107, or as a negative quantity with a positive
  price where your CIUS and the receiver accept it. Validate every generated invoice in CI with the official
  validator. Why: a credit line modelled as quantity 1 at a negative price renders fine as PDF and fails
  validation. Test: CI runs a pinned KoSIT validator with the XRechnung configuration (or the EN 16931
  schematron) over golden invoices for domestic, reverse charge, credit line, coupon, add-on and proration; any
  error fails the build. Source: EN 16931 BR-27, BR-28, BR-CO-11, https://github.com/itplr-kosit/validator
  (verified 2026-10).
- [invariant] For sellers and buyers established in Germany, domestic B2B invoices are electronic invoices in a
  structured format that conforms to EN 16931. Plan the output against the statutory dates: paper or other
  formats (with consent) end on 31 December 2026 for supplies in 2025 and 2026, and on 31 December 2027 for
  supplies in 2027 only when the issuer's previous-year turnover was at most EUR 800,000. Test: the
  invoice-output plan names the target date and syntax, and the validator step above exists before that date.
  Source: UStG § 14 and § 27 Abs. 38, https://www.gesetze-im-internet.de/ustg_1980/ (verified 2026-10).
- [invariant] Invoice lines have a deterministic order: an explicit position column and an `ORDER BY` on it.
  Why: lines came back in a different order on PostgreSQL than on the SQLite test database, so the PDF, the
  e-invoice and the golden file disagreed. Test: a golden-file test of the rendered invoice on PostgreSQL.
- [invariant] Generate invoices off the payment path: a unique job per transaction, an idempotent generator
  behind an interface, retries with backoff, a critical log on final failure, and a scheduled sweep that
  asserts every succeeded charge has exactly one invoice. Invoices are immutable and retained for 8 years
  from the end of the calendar year; erasure requests do not delete them. Test: two dispatches produce one
  invoice, and the sweep reports a charge without an invoice. Source: UStG § 14b Abs. 1, AO § 147 Abs. 3,
  GDPR Art. 17(3)(b), https://www.gesetze-im-internet.de/ustg_1980/__14b.html (verified 2026-10); retention
  versus erasure belongs to `gdpr-engineering`.

## Procedure

1. Gate: find the money path the change touches (amount, tax, charge, webhook, renewal, limit, invoice) and
   read the matching reference before writing code.
2. Read the PSP's docs at the installed SDK version, or a recorded response, before writing a handler or a
   fake. Cite the docs URL in the change. Without access, mark PSP facts unverified.
3. Put every amount through the one money helper and every tax decision through the one resolver.
4. Write the failure tests first: duplicates, concurrency, timeouts, amount mismatch, out-of-order events.
   Run them on PostgreSQL (or the production engine) and on the production runtime version.
5. For invoice output, render golden invoices and run the official validator over them.
6. Real charges, refunds or invoice sends during development go through `safe-actions`.
7. Add the guard artifacts that fit the repository.

## Traps

- A guard such as `if (percent <= 0) return;` written before fixed-amount coupons existed skips them
  silently. Grep for conditions on the old discount kind whenever a new kind is added.
- A suspended account resolved to the free plan inside the retention job, and the nightly cleanup deleted data
  the customer could still recover.
- An admin plan form with no preselected plan submits a downgrade when staff only meant to change another
  field. Preselect the current plan.
- A money test green on a developer host and red in the production image: the host ran a different PHP minor
  version. Pin the version once (for Composer, `config.platform.php`) and abort the suite on a mismatch.
- The SQLite test lane passed checks that PostgreSQL rejects: CHECK constraints, unique violations inside a
  transaction, row order. Billing tests that count run on PostgreSQL.

## Done when

- Amounts are integers or an exact type in one helper, with a property test and a runtime-version guard.
- The charged amount equals the invoice total for mixed baskets, and treatment, rate and VAT IDs are stored on
  each invoice.
- Reverse charge has tests for confirmed, invalid, unavailable and name mismatch, with stored proof.
- Webhooks have tests for forged, duplicate, parallel and out-of-order deliveries on PostgreSQL.
- Charges follow record-then-charge with a reconcile sweep; renewals claim per period.
- Limit checks pass the parallel-create test.
- Generated invoices pass the official validator in CI, and the missing-invoice sweep exists.

## References

- [references/money-and-rounding.md](references/money-and-rounding.md): load when computing any amount, VAT,
  proration or discount, or choosing a money library.
- [references/vat-eu-de.md](references/vat-eu-de.md): load for tax treatment, VAT IDs, reverse charge and the
  VIES response.
- [references/invoices-de.md](references/invoices-de.md): load for German invoice duties: reverse-charge
  wording, e-invoice dates, retention.
- [references/e-invoicing-en16931.md](references/e-invoicing-en16931.md): load for e-invoice output, credit
  notes, allowances, XRechnung or ZUGFeRD, and validator setup.
- [references/psp-webhooks.md](references/psp-webhooks.md): load when writing or reviewing a PSP webhook
  handler.
- [references/charge-lifecycle.md](references/charge-lifecycle.md): load for subscribe, renew, retry,
  reconcile, dunning and suspension.
- [references/plan-limits-and-quotas.md](references/plan-limits-and-quotas.md): load when adding a limit,
  enforcing a quota or changing downgrade behaviour.
- [references/coupons-and-price-locks.md](references/coupons-and-price-locks.md): load for discounts, price
  locks and campaign promises.
- [references/test-recipes.md](references/test-recipes.md): load when writing concurrency tests, recorded
  fixtures or transaction-level assertions.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the billing guards to a
  repository.

## Sources

- https://github.com/php/php-src/blob/PHP-8.4/UPGRADING: `round()` pre-rounding removed in PHP 8.4, verified
  2026-10.
- https://github.com/ConnectingEurope/eInvoicing-EN16931: EN 16931 validation artefacts (BR-27, BR-28,
  BR-CO-11, BR-CO-14, BR-CO-15, BR-CO-17, BR-AE-02, BR-AE-05, BR-AE-09, BR-AE-10), verified 2026-10.
- https://github.com/itplr-kosit/validator: KoSIT validator, Apache-2.0, verified 2026-10.
- https://ec.europa.eu/assets/taxud/vow-information/swagger_publicVAT.yaml: VIES response fields, verified
  2026-10.
- https://eur-lex.europa.eu/eli/dir/2006/112/oj: VAT Directive, Art. 44, 196, 226, verified 2026-10.
- https://www.gesetze-im-internet.de/ustg_1980/: UStG § 3a, § 14, § 14a, § 14b, § 27 Abs. 38, verified 2026-10.
- https://www.gesetze-im-internet.de/ao_1977/__147.html: AO § 147 retention periods, verified 2026-10.
- https://docs.mollie.com/reference/webhooks and https://docs.mollie.com/reference/api-idempotency: Mollie
  webhook and idempotency behaviour, verified 2026-10.
- https://docs.stripe.com/webhooks and https://docs.stripe.com/api/idempotent_requests: Stripe webhook and
  idempotency behaviour, verified 2026-10.
- https://www.postgresql.org/docs/current/sql-insert.html and
  https://www.postgresql.org/docs/current/functions-admin.html: ON CONFLICT and advisory locks, verified 2026-10.
