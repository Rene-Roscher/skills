---
name: build-vs-buy
description: "Decides what a SaaS builds in-house and what it takes from vendors or packages, and how it depends on them safely. Keeps business-critical rules (authorization, tenancy, plan limits, billing rules, audit) in-house and puts replaceable services (payments, mail, SMS, storage, DNS) behind an own interface with a fake, contract tests, a stored provider per resource and a documented exit. Covers dependency admission (license, maintenance, supply chain, data protection, blast radius), failover that fails visibly, third-party calls kept off critical write paths, caching upstream responses only when valid, and spend caps on paid channels. Use when adding a Composer, npm, Go or Python dependency or a SaaS provider, integrating a payment, mail or SMS gateway, designing provider failover, or when asked to build or buy, to evaluate a library, or whether to use a package for X. Not for pinning and signing CI actions, VAT and payment-state rules, or framework syntax."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Build vs buy

This skill decides which parts of a SaaS the team writes and owns, which parts it takes from a vendor or a
package, and how the code depends on what it takes. Vendor and SDK syntax stays in the vendor docs. It prevents
three failures: a business rule hidden in someone else's code, a dependency that fails silently, and a provider
that cannot be replaced when its price, terms or uptime change.

## Applies when / does not apply

- Applies: adding a Composer, npm, Go or Python dependency; adding or replacing a SaaS provider (payments, mail,
  SMS, voice, object storage, DNS, error tracking); designing provider failover; caching responses from a
  third-party API; questions such as "build or buy", "is there a package for X" or "evaluate this library".
- Does not apply: pinning and signing CI actions (`github-actions-hardening`), VAT, invoice and payment-state
  rules (`billing-eu-b2b`), framework upgrades, and framework or SDK syntax (read the vendor docs).

## Rules

### Decide and admit

- [default] Build in-house what encodes the product's own rules and carries security, correctness or money:
  authorization and roles, tenancy, plan and limit logic, billing rules and invoice content, audit trail,
  retention and deletion. Take commodity capabilities that several providers offer behind similar protocols
  (payment processing, mail delivery, SMS, object storage, DNS, error tracking) from vendors, behind an adapter.
  Record the decision in an ADR that answers the six questions in the decision criteria reference.
  Trade-off: owning the core costs build and maintenance time that a package would save. Deviate only with an
  ADR that names this trade-off. Proof: one ADR per core dependency and per provider.
- [invariant] Admit a dependency only after a recorded check of seven points: platform first (the framework or
  language already does it at the installed version), maintenance, license (an SPDX identifier; no license
  file means not admissible), supply chain (lockfile pinning, install scripts, transitive count, known
  vulnerabilities, provenance), blast radius (where it runs, what it can reach), personal data, and exit cost.
  Why: every dependency runs with your privileges, and an unlicensed or abandoned one cannot be fixed or
  redistributed. Test: diff the manifests between base and head; every added direct dependency has an
  admission record with all seven answers, otherwise the change is rejected.
  Source: https://github.com/ossf/scorecard/blob/main/docs/checks.md (verified 2026-10).
- [default] Keep a committed dependency register with one entry per direct dependency: purpose, license,
  owner, data it touches, exit. Trade-off: one more file to keep current, and friction on every new package.
  Deviate only with an ADR that names this trade-off. Proof: a script lists direct dependencies from the
  manifests that have no register entry, and the list is empty.
- [invariant] State no provider or package fact from memory. Field names, status codes, webhook semantics, rate
  limits, SDK methods, license and maintenance status come from the provider's docs at the installed version
  or from a recorded real response; anything unchecked is marked unverified in the same sentence. Why: a fake
  built from a remembered field name passes the suite and fails in production. Test: every recorded fixture
  file names its source (docs URL or recorded call) and date, and a lint fails on fixtures without that
  header. Source: docs routing is owned by `evidence-before-claims`; the first trap below shows the failure.

### Fail visibly

- [invariant] An adapter or dispatcher that receives an unsupported channel, method or capability throws. It
  never returns a synthetic success and never records "sent" without handing the message to a provider. Keep
  one dispatch path per capability, so a new channel is added in one place. Why: with duplicated dispatch
  code, a new channel lands in one copy while the other reports success for messages nobody sent. Test:
  dispatch to an unregistered channel through every entry point (immediate and delayed); expect an exception
  and no "sent" record.
- [invariant] A failover chain for messages someone depends on (alerts, password resets, invoices) never ends
  in a log, null or array transport. When every real provider fails, the send fails: exception, queue retry,
  dead-letter record and an operator alert. Why: a log transport accepts every message and reports it as sent,
  so an outage of all providers turns into silent success. Test: make every real transport throw; expect a
  failed job, a dead-letter record and an alert. Source: laravel/framework v12.53.0
  `Mail/Transport/LogTransport::send()` writes the message to the debug log and returns a `SentMessage`;
  symfony/mailer v7.4.6 `RoundRobinTransport::send()` throws "All transports failed." only when no transport
  succeeded (vendor source read 2026-10-31).
- [invariant] Commit the local record before any irreversible provider call, and run non-critical downstream
  integrations (accounting, CRM, analytics, document rendering) as their own idempotent, unique jobs with
  retries and a scheduled reconcile sweep. Why: an outage of the accounting API must not block a booking, roll
  back a payment record or leave a charge without its follow-up work. Test: make the downstream adapter throw;
  the core action succeeds, a job is queued, and the sweep picks it up later. Source: reproducible by the
  test; money-specific rules (idempotency keys, webhook re-fetch) live in `billing-eu-b2b`.
- [default] Before relying on a library's failover, write into the ADR where the "dead provider" state lives
  (per process or shared), whether it fails back on its own, and how long a failing primary delays each send.
  Set tight connect and request timeouts on the primary, emit success and failure metrics per provider, and
  alert when traffic moves to the secondary. Trade-off: extra metrics and one staging drill per chain. Deviate
  only with an ADR that names this trade-off. Source: symfony/mailer v7.4.6 `FailoverTransport` and
  `RoundRobinTransport` (vendor source read 2026-10-31), summarised in the failover reference.
- [default] Alerts, transactional mail and marketing mail use separate provider chains, with separate sender
  domains or streams and independent failure tracking. Trade-off: more provider accounts, DNS records and
  config. Deviate only with an ADR that names this trade-off. Proof: a config test asserts which chain each
  message class uses and that the alert chain contains no marketing stream.
- [default] Cache a third-party response only after validating it. On an invalid response, cache a fallback
  for a bounded retry window so a broken upstream is not called on every request, and take a lock against
  stampedes. Trade-off: a validator per upstream, and a fallback value that can be stale. Deviate only with an
  ADR that names this trade-off. Proof: an invalid response is not stored as the value; inside the retry
  window the upstream is not called again; after it, it is. Source:
  https://github.com/Rene-Roscher/conditional-cache-laravel (one Laravel implementation, verified 2026-10).

### Shape the adapter

- [default] The domain depends on an own interface per capability (for example `PaymentProvider`,
  `SmsGateway`, `ObjectStore`) with its own request and result types and provider-neutral status enums. Vendor
  SDK classes appear only inside the adapter namespace. Where providers differ in kind, expose capability
  flags (such as "manages the subscription cycle") and branch on those, never on the adapter class.
  Trade-off: a translation layer to write and keep in step with each SDK. Deviate only with an ADR that names
  this trade-off. Proof: an architecture test fails when the SDK namespace is used outside the adapters
  namespace. Source: https://alistair.cockburn.us/hexagonal-architecture/ (verified 2026-10).
- [default] Each interface has one contract test suite that runs against the fake on every build and against
  the provider's sandbox on a schedule or in an opt-in job. The fake covers the edge cases the contract names
  (decline, timeout, unknown ID, duplicate webhook), not only success. Trade-off: sandbox accounts and a
  scheduled job to keep green. Deviate only with an ADR that names this trade-off. Proof: one test dataset
  parameterised over every registered adapter, and CI shows the date of the last green sandbox run.
- [default] Store the provider on each resource it handled (subscription, payment, mandate, message) and pick
  the adapter from the stored value, so new work can go to a new provider while existing resources finish on
  the old one. Trade-off: a column and a resolver on every provider-backed table. Deviate only with an ADR that
  names this trade-off. Proof: two resources with different stored providers resolve to different adapters,
  and an unknown value throws.
- [default] Document the exit for every provider behind an adapter: data export, dual run, a cut-over flag, and
  what cannot move. Check the provider's docs for whether stored payment credentials, mandates and customer
  objects can be exported; where the docs don't say, plan for customers entering payment details again.
  Rehearse the switch once in a test environment. Trade-off: time spent on a migration that may never happen.
  Deviate only with an ADR that names this trade-off. Proof: the exit section of the provider ADR carries the
  date of the last rehearsal.

### Cost and personal data

- [default] Paid outbound adapters (SMS, voice, paid messaging) enforce caps at the adapter boundary: per
  recipient, per tenant with a hard ceiling, and a global breaker that stops sending. Automatic credit top-up
  refuses while a cap or the breaker is active. Trade-off: a legitimate burst can hit a cap and needs an
  operator to lift it. Deviate only with an ADR that names this trade-off. Proof: one test per cap level and
  one for top-up refusal while frozen.
- [default] A new provider or embed that receives personal data or visitor IP addresses is a compliance event:
  processor role and AVV (data processing agreement), subprocessor list, VVT (record of processing activities)
  entry, third-country transfer check, privacy notice. Derive the provider inventory from code (provider
  enums, config, sender services) and compare it with the subprocessor register. Third-party embeds such as
  avatars, fonts, analytics and chat widgets count. Trade-off: legal review delays a provider switch. Deviate
  only with an ADR that names this trade-off. Proof: a script lists the providers found in config and enums
  and fails when one is missing from the register. Details belong to `gdpr-engineering`.

## Procedure

1. Gate: classify the request. Is it a product rule or a commodity capability? Answer the six questions and
   write the ADR before writing code.
2. Platform first: look up whether the framework or language already covers it, in the docs for the version in
   the lockfile.
3. For a package, run the admission checklist with the audit and license commands of its ecosystem. Without
   network or docs access, mark license and maintenance status unverified and say so in the answer.
4. For a provider, define the interface and its types, write the fake and the contract suite, and add the
   provider column and resolver. Fixtures come from recorded responses only.
5. Check the failure behaviour: one dispatch path, unknown capability throws, the failover chain ends in a
   visible failure, downstream calls stay off the write path, caching stores only validated responses.
6. Paid channels get caps and a breaker. Personal data starts the compliance checklist in `gdpr-engineering`.
7. Write the exit section of the ADR, then add the guard artifacts that fit the repository.

## Traps

- A fake built from memory. A tax-ID check read a field name the registry API does not return, and the fake
  returned the same name, so the suite passed while production read every valid ID as invalid. Detect it by
  comparing fixtures with one recorded real response.
- Two dispatch paths. Immediate and delayed delivery lived in two job classes; a new channel was added to one,
  and the other recorded "sent" for messages it never handed to a provider. Detect it by listing every caller
  of the adapters' send methods; more than one is a finding.
- `log` as the last failover entry "so nothing gets lost". It reports every message as sent, so a full
  provider outage looks like normal operation.
- Sticky failover in long-lived processes. Symfony's failover transport stays on the secondary for as long as
  the secondary works, and the framework can keep the resolved mailer for the life of the worker. One short
  primary outage can move all mail to the secondary until a restart.
- A provider switched in one place only. Webhooks for existing subscriptions still arrive for the old provider;
  without a stored provider per resource they hit the new adapter and fail.
- Activity metrics read as proof. Frequent commits say nothing about how security reports are handled. Read
  the security policy and the advisory history as well.
- A subprocessor list kept by hand falls behind the providers added in code. Derive the list from code.

## Done when

- The ADR exists, answers the six questions and contains the exit section.
- Every new direct dependency has an admission record, and the audit and license checks ran clean or their
  findings are written down.
- Provider code has an interface, a fake, a contract suite, a provider column and an architecture test.
- Failure tests exist: unknown channel throws, all providers down fails visibly, a downstream outage leaves the
  core action intact.
- Paid channels have cap tests, and a provider that receives personal data has its compliance checklist done.

## References

- [references/decision-criteria.md](references/decision-criteria.md): load when deciding build or buy, or when
  writing the ADR (six questions, typical outcomes, template).
- [references/dependency-admission.md](references/dependency-admission.md): load when adding any package or
  provider (checklist, admission record, audit and license commands per ecosystem).
- [references/adapter-pattern.md](references/adapter-pattern.md): load when integrating a provider (interface,
  types, capability flags, fake, contract tests, provider column, exit).
- [references/failover.md](references/failover.md): load when designing failover for mail, SMS or payments
  (library mechanics with verification dates, drills).
- [references/stack-laravel.md](references/stack-laravel.md): load in a Laravel project (failover mailers,
  resolver binding, Pest architecture rules, validated caching).
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the CI and test guards to a
  repository.

## Sources

- https://github.com/ossf/scorecard/blob/main/docs/checks.md: maintenance, license and supply-chain signals,
  verified 2026-10.
- https://alistair.cockburn.us/hexagonal-architecture/: ports and adapters, verified 2026-10.
- https://laravel.com/docs/12.x/mail#failover-configuration: failover mailer configuration, verified 2026-10.
- laravel/framework v12.53.0 (`LogTransport`, `MailManager`) and symfony/mailer v7.4.6 (`FailoverTransport`,
  `RoundRobinTransport`): vendor source read 2026-10-31.
- https://github.com/Rene-Roscher/conditional-cache-laravel: validated caching, retry window and lock, MIT,
  verified 2026-10.
- https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck and https://google.github.io/osv-scanner/usage/:
  vulnerability scanners, verified 2026-10.
- https://pestphp.com/docs/arch-testing: architecture expectations, verified 2026-10.
