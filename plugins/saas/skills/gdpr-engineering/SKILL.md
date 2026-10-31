---
name: gdpr-engineering
description: "Builds GDPR (DSGVO) compliance into EU SaaS features: controller or processor role, when to update the VVT, AVV, subprocessor list, TOM, privacy notice or DPIA, deletion, retention and export in code. Use when a change adds personal data, a third-party service or SDK, a retention period, data leaving the EU, Art. 9 data, tracking or email, or asked if X is GDPR-compliant. Not for legal advice."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
  jurisdiction: "EU, DE specifics"
  disclaimer: "Review-ready draft, not legal advice"
  verified: "2026-10"
---

# GDPR engineering

This skill turns privacy duties into files and tests that change together with the code: who is responsible for
which data, which documents a change touches, and how deletion, retention, exports and logs are proven. Contract
wording and legal judgement stay with counsel. The failure it prevents: privacy texts and records that describe a
product that no longer exists, and personal data that survives deletion or leaks into logs.

Review-ready draft, not legal advice. Scope: EU (GDPR, DSA) with German specifics (TDDDG, UWG, UStG, AO). Statute
text checked against the official sources on 2026-10-31. German working terms stay German: AVV (DPA, Art. 28), VVT
(record of processing, Art. 30), TOM (technical and organisational measures, Art. 32), DSFA (DPIA, Art. 35).

## Applies when / does not apply

- Applies: a plan, migration or pull request adds a personal-data column or free-text field (including free text
  arriving from customer systems), a third-party service, SDK, notification channel or outbound host, a retention
  period or cleanup job, processing outside the EU/EEA, Art. 9 data, user-generated or public content,
  promotional or lifecycle email, cookies or device storage, avatars or embeds, error-tracker or logging setup,
  account or tenant deletion, or a data export. Also when someone asks whether something is GDPR-compliant.
- Does not apply: drafting contracts or giving legal advice, generic security audits, non-EU regimes (CCPA,
  HIPAA). Neighbours: `tenant-isolation` (cross-tenant leaks in exports and caches), `dual-key-identifiers` (no
  internal IDs in exports), `safe-actions` (approval before touching production data or notifying customers),
  `billing-eu-b2b` (invoice content), `evidence-before-claims` (checking any citation).

## Rules

### Role and triggers

- [invariant] Decide the role per data set before designing: processor (your customer is the controller) or
  controller (your own purposes). Processor data needs the AVV, TOM, subprocessor annex and the processor VVT;
  controller data (signup, billing, your own analytics, support requests, content users post on your own
  surfaces) needs the privacy notice, the controller VVT and a legal basis per purpose.
  Why: most errors here start with the wrong role; content posted on your own board makes you the controller, so
  it belongs in the privacy notice and VVT, not in the AVV.
  Test: every entry in `privacy/inventory.yaml` carries role, purpose, legal basis, data subjects, recipients,
  retention and location; CI fails when a migration adds a column annotated or named as personal data without an
  entry. Source: GDPR Art. 6, 13, 28(1)-(4), 30(1)-(2), https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [invariant] Run the trigger table below on every plan and pull request. Each hit names the artifact to update
  before merge; no hit gets a one-line "privacy: no change" reason.
  Why: privacy work that the change itself does not trigger happens months later, when the text already
  contradicts the product.
  Test: a pull request that touches a migration, mail or notification class, SDK manifest or outbound host config
  without an inventory change or a "no change" note fails the CI label check.
  Source: GDPR Art. 28(2), 30(1)(c)-(g), 35(1), https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

| Trigger in the change | Update |
|---|---|
| New personal-data column, free-text field, or free text from customer systems (logs, agent output) | inventory, VVT, AVV data categories |
| New third-party service, SDK, provider account you hold, outbound host, notification channel | subprocessor list and AVV annex (for processor data), privacy notice, transfer check |
| New or changed retention period, cleanup job, backup window | retention schedule, VVT (Art. 30(1)(f)), TOM |
| Processing or support access outside the EU/EEA, including a subprocessor's own subprocessors | transfer basis (Chapter V), subprocessor list |
| Art. 9 or Art. 10 data | DSFA triage, VVT, access restriction |
| User-generated or public content | privacy notice (you are controller), DSA duties |
| Marketing, lifecycle or review-request email | purpose separation, consent or exception record |
| Cookies, local storage, device fingerprinting | TDDDG § 25 consent check |
| Profiling, scoring, automated decisions | DSFA triage |

### Artifacts follow the code

- [invariant] Legal text never promises more than the code does. Every number and claim in the privacy notice,
  TOM and AVV traces to a config value or code path.
  Why: a stated retention period or hosting location that no setting enforces is a false statement to every
  customer who reads it.
  Test: `privacy/claims.yaml` maps each claim to a config key and the expected value; a test reads the runtime
  config and fails on any mismatch. Source: GDPR Art. 5(1)(a), 13, https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [invariant] Derive the subprocessor list from code, not from legal texts. A provider account you hold
  (messaging, push, mail, error tracking, storage) is a subprocessor; an endpoint the customer points at, such as
  their own chat webhook, is customer-directed and is not. List the contracting entity and the processing country.
  Follow your AVV's change procedure before a new subprocessor goes live: the statute requires informing the
  controller and giving the chance to object, and the notice period comes from your AVV.
  Why: lists written from memory miss providers the code calls.
  Test: a test maps every outbound integration class, SDK and configured host to an entry in
  `privacy/subprocessors.yaml` with `customer_directed`, entity, country and transfer basis, and fails on any
  unmapped one. Source: GDPR Art. 28(2), 28(4), https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [invariant] Version binding documents from the text that is rendered live. Deploy the new text first, then bump
  the version that forces re-acceptance.
  Why: an edited copy that is not the rendered source changes nothing, and a text change without a version bump
  never reaches existing customers.
  Test: one config holds document versions and URLs; a scheduled check requests every legal URL in every offered
  language and fails on any status other than 200.

### Logs, error trackers and error messages

- [invariant] No personal data or secrets in logs, error-tracker events or user-facing errors. Mask client IPs
  (for example /24 for IPv4, /48 for IPv6), log a short hash prefix of a token instead of the token or its full
  hash, and forward only curated messages from typed domain exceptions to browsers, API clients, workers and
  delivery logs.
  Why: raw exception text and stack-frame arguments carry tokens, emails and query values to every place an error
  is shown or stored.
  Test: trigger a connection error on an authenticated HTTP client with a fake error-tracker transport; the
  captured event contains no token. A failing export stores a generic message, not the exception text.
  Source: GDPR Art. 5(1)(c), 32(1); https://docs.sentry.io/platforms/php/data-management/data-collection/ (verified 2026-10).

- [default] Set `zend.exception_ignore_args=On` in the production image. Accepted alternative: turn off
  stack-frame variables in the error-tracker SDK and scrub events in `before_send`. Mark secret parameters
  `#[\SensitiveParameter]` (PHP 8.2 and later) in both cases.
  Trade-off: stack traces lose argument values that help debugging. Deviate only with an ADR that names this
  trade-off. Test: `php -r 'exit(ini_get("zend.exception_ignore_args") ? 0 : 1);'` exits 0 inside the production
  image. Source: https://www.php.net/manual/en/ini.core.php, https://www.php.net/manual/en/class.sensitiveparameter.php (verified 2026-10).

### Deletion, retention and exports

- [invariant] Erasure is complete and proven. Deleting an account or tenant removes or scrubs every copy: rows,
  denormalised snapshots (a delivery log that copied a recipient's email), audit subject labels, object-storage
  prefixes (exports, imports, generated PDFs), caches and search indexes. Foreign keys to people use
  `ON DELETE SET NULL` or cascade by design, never `RESTRICT`. Document the backup rotation window after which
  erased data is gone.
  Why: a `RESTRICT` key blocks the erasure forever, and copies outside the main table survive it.
  Test: seed one person into every table and storage prefix the inventory lists, run the erasure, then search a
  database dump and the storage listing for the email and the name: zero hits.
  Source: GDPR Art. 17(1), https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [invariant] Retention runs as a scheduled, tenant-scoped job driven by one resolver, with documented windows.
  Recoverable states (suspended, past due) keep the window they are entitled to and never fall back to a
  free-plan window. Legal retention duties override erasure: keep the record, restrict access and clear the
  fields the duty does not need. In Germany invoices stay 8 years from the end of the calendar year of issue
  (UStG § 14b Abs. 1), other records 10, 8 or 6 years by class (AO § 147 Abs. 3).
  Why: a cleanup that reads the wrong window deletes data the customer still pays for, and one without a legal
  floor deletes records the business must keep.
  Test: per plan and per account state, records just inside the window survive the job and records just outside
  are gone; an invoice survives account erasure with its non-required personal fields cleared.
  Source: GDPR Art. 5(1)(e), 17(3)(b); https://www.gesetze-im-internet.de/ustg_1980/__14b.html,
  https://www.gesetze-im-internet.de/ao_1977/__147.html (verified 2026-10).

- [default] Build data-subject request tooling before the first request: an export for access and portability,
  generated asynchronously behind a signed, expiring URL, authorised against the requesting person or tenant
  (never a "current tenant" fallback), without internal sequential IDs, plus a deadline tracker.
  Trade-off: tooling built ahead of demand that a manual process could cover at low volume. Deviate only with an
  ADR that names this trade-off. Test: tenant B cannot download tenant A's export (404); unzipping the archive and
  scanning it finds no integer `id` fields. Source: GDPR Art. 12(3) (one month, extendable by two further months),
  15, 20, https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [default] Keep breach readiness in the repo: a runbook with the 72-hour clock and its decision points, a named
  owner, and an access log for personal-data exports and admin impersonation.
  Trade-off: a document and a log that need upkeep and are rarely used. Deviate only with an ADR that names this
  trade-off. Source: GDPR Art. 33(1) ("not later than 72 hours after having become aware of it"), 34(1),
  https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

### Specific triggers

- [invariant] No third-party avatar or tracking embeds that send each viewer's request to a third party. Use
  initials or images you host.
  Why: a hashed email is pseudonymous, not anonymous, and every image request carries the viewer's IP address to
  a new recipient, possibly outside the EU.
  Test: the CSP `img-src` lists no third-party avatar host; a lint rule rejects an email hash (`md5(` or
  `sha256(` of an email) in an image URL. Source: GDPR Recital 26, Art. 44, https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [invariant] Recognise Art. 9 data in design and minimise it. An absence reason "sick" in a staffing or
  shift-planning feature is health data: colleagues see a neutral form ("unavailable"), only the roles that need
  the reason can read it, and the Art. 9(2) exception you rely on, a DSFA triage and a VVT entry are recorded.
  The small-company exemption in Art. 30(5) does not apply when processing is not occasional or includes Art. 9
  data, which is the normal case for a SaaS.
  Test: a colleague's API response carries only the neutral form; a policy test shows only authorised roles read
  the reason. Source: GDPR Art. 9(1), 30(5), 35(3)(b), https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

- [default] Triage every new processing activity for a DSFA against the nine WP248 criteria and record the result
  in the VVT. Two or more criteria: plan a DSFA. Also check your supervisory authority's Art. 35(4) list.
  Trade-off: a short note per feature, even when the answer is no. Deviate only with an ADR that names this
  trade-off. Source: Article 29 Working Party, WP248 rev.01, https://ec.europa.eu/newsroom/article29/items/611236;
  GDPR Art. 35(1), (3), (4) (verified 2026-10).

- [invariant] Every outbound message carries a purpose (transactional, service, promotional), and the dispatcher
  enforces it. Promotional email needs prior consent or, in Germany, all four conditions of the existing-customer
  exception; this covers B2B recipients too. Contact data collected for operational notifications never feeds
  promotion. No open-tracking pixels by default.
  Test: sending a promotional message without a consent or exception record throws; promotional mail carries an
  opt-out link and a `List-Unsubscribe` header. Source: UWG § 7 Abs. 2 Nr. 2, Abs. 3,
  https://www.gesetze-im-internet.de/uwg_2004/__7.html; GDPR Art. 5(1)(b) (verified 2026-10).

- [invariant] Hosting user content brings DSA duties, also for micro and small companies: notice and action
  (Art. 16), a statement of reasons for any restriction including demotion or hiding (Art. 17), and moderation
  rules in the terms (Art. 14). The Art. 19 exemption covers only the online-platform section. Login-only
  visibility does not remove these duties. A person's name is shown publicly only with consent or as a display
  name they chose.
  Test: a notice sent to the endpoint creates a moderation record with the reason, the terms clause and whether
  the decision was automated. Source: Regulation (EU) 2022/2065 Art. 14, 16, 17, 19,
  https://eur-lex.europa.eu/eli/reg/2022/2065/oj (verified 2026-10).

- [invariant] Processing or remote access outside the EU/EEA needs a Chapter V basis, and defaults in code match
  the contracts: a location the contract calls opt-in is never selected by default.
  Test: locations carry a `third_country` flag; the default selection returns only EU/EEA or adequacy locations;
  each subprocessor entry records its transfer basis. Source: GDPR Art. 44-46; adequacy list
  https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en (verified 2026-10).

- [invariant] Storing or reading anything on the user's device needs consent, unless it is strictly necessary for
  a service the user explicitly asked for.
  Test: a browser test lists cookies and local and session storage keys before any consent and compares them
  with an allowlist that gives a reason per key. Source: TDDDG § 25 Abs. 1, Abs. 2 Nr. 2,
  https://www.gesetze-im-internet.de/ttdsg/__25.html (verified 2026-10).

- [invariant] Personal data from production does not enter development or test environments. Use synthetic
  factories. If an incident makes a production copy unavoidable, it needs approval through `safe-actions`, a file
  with mode 0600, deletion after use, and env files restored byte for byte.
  Test: a lint over seeders and fixtures rejects email domains outside example.com, example.org and example.net.
  Source: GDPR Art. 5(1)(b)-(c), 25, https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

## Procedure

1. Gate: check the change against the trigger table. No hit: write "privacy: no change" and the reason into the
   plan or pull request, and stop.
2. For each data set the change touches, decide the role and update `privacy/inventory.yaml`.
3. For each new provider or host, classify it as customer-directed or subprocessor and record entity, country and
   transfer basis. A new subprocessor goes through the AVV change procedure before go-live; sending that notice
   to customers is an external action under `safe-actions`.
4. Add or extend the guard tests the hit calls for (erasure, retention, claims, scrubbing, export isolation).
   Run the erasure and retention tests on the production database engine.
5. Update the legal texts from the inventory and the claims manifest. Deploy the text, then bump its version.
6. Before citing an article, a court decision or authority guidance, fetch the primary source and write the date
   next to the citation. Anything not fetched is marked Unverified.
7. Hand the drafts to the person who signs off, labelled "review-ready draft, not legal advice".

## Traps

- Sentry PHP sends local variables with errors by default (`stack_frame_variables` defaults to true), so a token
  passed as an argument ships with the event. `zend.exception_ignore_args=1` stops PHP from providing them.
- Passing a Sentry `data_collection` array opts into permissive defaults for every key you leave out (user,
  cookies, request and response bodies), and `send_default_pii` is then ignored. The docs name different first
  versions for the option (4.29.0 on the Laravel guide, 4.33.0 on the PHP page, checked 2026-10-31): read the
  installed version from the lockfile before configuring it.
- Debug dumpers can print values a closure captured in its `use` list. Resolve the secret inside the closure at
  call time instead. Check it: dump the closure; the output must not contain the secret.
- Unsubscribing deletes the subscriber, but a delivery log that copied the address keeps it.
- Review-request emails may count as advertising. Ask counsel; do not cite court decisions from memory.
- "Fewer than 250 employees, so no VVT" ignores the two exceptions in Art. 30(5) that a SaaS almost always meets.
- An export job that resolves the tenant from session or a "current tenant" helper serves the wrong tenant when
  it runs in a queue.
- Internal copies of legal texts look authoritative but are not what customers see. Only the rendered version
  counts.

## Done when

- The pull request answers the trigger table: each hit with its updated artifact, or "no change" with a reason.
- Inventory, subprocessor list and claims manifest match the code, and their coverage tests pass.
- Erasure and retention tests pass on the production database engine.
- Legal text drafts carry dated primary sources and the review-ready label, and the signer has them.

## References

- [references/role-and-artifacts.md](references/role-and-artifacts.md): load when deciding controller or processor,
  or which document a role needs.
- [references/inventory-templates.md](references/inventory-templates.md): load when creating `inventory.yaml`,
  `subprocessors.yaml` or `claims.yaml` and their coverage tests.
- [references/deletion-and-retention.md](references/deletion-and-retention.md): load when building erasure flows,
  retention jobs, legal holds or backup windows.
- [references/retention-periods-de.md](references/retention-periods-de.md): load when a German tax or commercial
  retention duty applies (UStG, AO).
- [references/logging-and-error-trackers.md](references/logging-and-error-trackers.md): load when configuring logs,
  Sentry or a similar error tracker.
- [references/subprocessors-and-transfers.md](references/subprocessors-and-transfers.md): load when adding a
  provider, changing regions or checking a Chapter V basis.
- [references/dpia-triage.md](references/dpia-triage.md): load when new processing might be high risk.
- [references/marketing-and-device-storage-de.md](references/marketing-and-device-storage-de.md): load for
  promotional or lifecycle email (UWG § 7) and cookies or device storage (TDDDG § 25).
- [references/ugc-dsa.md](references/ugc-dsa.md): load for comments, boards, public profiles and moderation.
- [references/glossary-de-en.md](references/glossary-de-en.md): load when German and English terms need mapping.
- [references/source-hygiene.md](references/source-hygiene.md): load before citing any article, case or authority
  guidance.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when wiring the guard tests, the pull
  request template or a path-scoped rule that points here.

## Sources

- https://eur-lex.europa.eu/eli/reg/2016/679/oj: GDPR, Art. 5, 6, 9, 12, 13, 15, 17, 20, 25, 28, 30, 32-35, 44-46,
  Recital 26, verified 2026-10.
- https://eur-lex.europa.eu/eli/reg/2022/2065/oj: Digital Services Act, Art. 14, 16, 17, 19, verified 2026-10.
- https://ec.europa.eu/newsroom/article29/items/611236: WP248 rev.01, DPIA guidelines, verified 2026-10.
- https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en:
  current adequacy decisions, verified 2026-10.
- https://www.gesetze-im-internet.de/uwg_2004/__7.html: UWG § 7, verified 2026-10.
- https://www.gesetze-im-internet.de/ttdsg/__25.html: TDDDG § 25, verified 2026-10.
- https://www.gesetze-im-internet.de/ustg_1980/__14b.html: UStG § 14b, verified 2026-10.
- https://www.gesetze-im-internet.de/ao_1977/__147.html: AO § 147, verified 2026-10.
- https://www.php.net/manual/en/ini.core.php: `zend.exception_ignore_args`, verified 2026-10.
- https://www.php.net/manual/en/class.sensitiveparameter.php: `SensitiveParameter`, verified 2026-10.
- https://docs.sentry.io/platforms/php/data-management/data-collection/ and
  https://docs.sentry.io/platforms/php/guides/laravel/configuration/options/: stack-frame variables,
  `data_collection`, `send_default_pii`, verified 2026-10.
