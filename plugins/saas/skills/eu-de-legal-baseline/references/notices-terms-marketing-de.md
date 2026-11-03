# Notices, terms and marketing in Germany

Review-ready draft, not legal advice. Scope: Germany. Statute text read on gesetze-im-internet.de on 2026-11-03.

## Impressum (DDG § 5)

- The Digitale-Dienste-Gesetz (DDG) carries the provider-identification duty that used to sit in the
  Telemediengesetz. The DDG text on gesetze-im-internet.de is valid from 14 May 2024; the TMG is no longer
  listed there (checked 2026-11-03).
- Who: providers of "geschäftsmäßige, in der Regel gegen Entgelt angebotene digitale Dienste". A B2B SaaS, its
  marketing site and its help centre are such services.
- How: the information must be "leicht erkennbar und unmittelbar erreichbar" and kept "ständig verfügbar".
  Engineering reading: a link labelled "Impressum" (German pages) or "Legal notice" (English pages) in the
  footer or menu of every page and app screen, one click, no login, not hidden behind a consent banner.
- What (Abs. 1 Nr. 1-8, summarised): name and address of establishment; for legal entities legal form,
  representatives and, where stated, capital; fast electronic contact including an email address; supervisory
  authority if the activity needs a licence; register and register number; for regulated professions chamber,
  title and rules; VAT ID or business ID if any; liquidation notice where relevant.
- Surfaces to cover: website, web app (including the login page), mobile apps (store listing and in-app), help
  centre, public status and marketing pages, newsletter footers, commercial social profiles. Social profiles
  are treated as separate services in common practice; no primary source was fetched for that point
  (Unverified). A link from each profile's info field to the Impressum is the low-cost route.
- Journalistic or editorial content (company blog, newsletter with editorial content) can bring a separate
  duty to name a responsible person under the Medienstaatsvertrag. Not checked against the treaty text
  (Unverified); ask the lawyer when the blog is more than product news.
- Keep the data in one source (config or CMS entry) and render it everywhere, so a change of address or
  managing director reaches every surface.

## Cookies, device storage and analytics (TDDDG § 25)

- Abs. 1: storing information on the end user's device, or reading information already stored there, needs
  consent based on clear and full information, given in line with the GDPR.
- Abs. 2 Nr. 2: no consent where the storage or access is "unbedingt erforderlich" so that the provider can
  supply a digital service the user explicitly asked for. A session cookie for a logged-in app, a CSRF token
  and a stored consent choice are typical examples; analytics, A/B testing and marketing tags are not.
- The law was renamed from TTDSG to TDDDG; the URL still reads `ttdsg`.
- EDPB Guidelines 2/2023 (v2.0, adopted 7 October 2024) read the underlying Art. 5(3) ePrivacy Directive
  broadly: tracking pixels, tracking links and some forms of local processing can count as gaining access to
  the device. "Cookieless" in a vendor brochure does not answer the question.
- Analytics without consent is defensible only when it neither stores nor reads anything on the device beyond
  what the request itself carries, and the GDPR side (legal basis, VVT, IP handling) is settled in
  `gdpr-engineering`. Record the decision and the tool configuration that supports it.
- Test method: a headless browser loads every public page and the app shell without consent and lists cookies,
  local storage, session storage, IndexedDB and outgoing requests; the CI job compares them with an allowlist
  that names a reason per key.

## AGB (BGB §§ 305-310)

- Incorporation with consumers (§ 305 Abs. 2): an express reference at conclusion, a reasonable chance to read
  them, and the customer's agreement. Build it as a checkbox or a button text that names the terms, next to a
  link that opens the exact version being accepted.
- B2B (§ 310 Abs. 1): § 305 Abs. 2 and 3, § 308 Nr. 1, 2-9 and § 309 do not apply directly, but § 307 does,
  including where it leads to the invalidity of clauses those sections list. How far §§ 308 and 309 still
  guide the § 307 review in B2B is case law, not checked here (Unverified); ask the lawyer.
- Surprising clauses do not become part of the contract, and ambiguity is read against the drafter
  (§ 305c Abs. 1, 2). Engineering consequence: the plan limits and service levels that the product enforces
  must match the terms word for word.
- Changes: a reserved right to change the service is void unless the change is reasonable for the customer
  (§ 308 Nr. 4); deemed consent by silence needs a reasonable deadline and an explicit notice of what silence
  means (§ 308 Nr. 5). Default to asking for new agreement for material changes. A lawyer approves any change
  clause.
- Data model: `legal_documents(id, kind, version, published_at, body_ref)`, `acceptances(account_id or
  user_id, document_id, accepted_at, context)`. The rendered page reads the same row the acceptance points to.

## Marketing claims, comparisons and reviews (UWG)

- § 5 Abs. 1: a misleading commercial practice that can make a consumer or other market participant decide
  differently is unfair. Abs. 2 lists untrue or deceptive statements about features, expected results, test
  results, price, the trader's status, approvals and awards. Business buyers are protected too.
- Claims that need an evidence file: uptime or performance numbers, "fastest", "only", "number one",
  "certified", "ISO", "GDPR-compliant", "hosted in Germany", customer or user counts, savings figures, logos of
  customers (with permission on file).
- § 6: comparative advertising is any advertising that makes a competitor or its products identifiable. It is
  unfair, among other things, when it compares products that do not meet the same need, is not objective about
  essential, relevant, verifiable and typical features or price, creates confusion, exploits or harms a
  competitor's mark, or disparages. A comparison page keeps a dated source per competitor fact and gets a
  lawyer's review before publishing.
- Reviews: § 5b Abs. 3 makes information on whether and how the trader ensures reviews come from real users
  material. Anhang Nr. 23b (claiming reviews are genuine without reasonable checks) and Nr. 23c (submitting or
  commissioning fake reviews, misrepresenting reviews on social media) are always unfair.
- Asking customers for reviews by email can be advertising under UWG § 7; see `gdpr-engineering` for the email
  rules.
