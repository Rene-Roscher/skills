---
name: eu-de-legal-baseline
description: "Spots when a SaaS change touches German or EU law and routes it: Impressum, cookies, consumer sign-up, AGB, UWG claims, reviews and § 7 outreach, BFSG accessibility, DSA, Data Act switching, NIS2, CRA, AI Act, retention. Use when planning a launch, sign-up, pricing, marketing claim, outreach, user content or AI feature. Not legal advice; GDPR goes to gdpr-engineering, VAT and invoices to billing-eu-b2b."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
  jurisdiction: "DE, EU"
  disclaimer: "Review-ready draft, not legal or tax advice"
  verified: "2026-11-03"
---

# EU and German legal baseline

This skill decides which German or EU legal duty a product change touches, what the baseline obligation is, and
who has to look at it next: another skill, a lawyer, or a tax adviser. It covers a SaaS run from Germany for EU
customers, mostly B2B and sometimes open to consumers. It does not draft contracts or give legal conclusions.
The failure it prevents: a feature or launch that ships without the notice, button, contract clause or
registration the law attached to it, and an agent that tells the team "this is compliant" when nobody with the
standing to say so has looked.

Review-ready draft, not legal or tax advice. Scope: Germany and the EU. Statutes were read on
gesetze-im-internet.de, regulations on EUR-Lex (Official Journal text) and authority pages on 2026-11-03.
Statements that could not be checked against a primary source are marked Unverified. German terms that must stay
German stay German: Impressum (provider identification), AGB (standard business terms), Widerrufsrecht (consumer
right of withdrawal), Kündigungsbutton (cancellation button), AVV (data processing agreement).

## Applies when / does not apply

- Applies: a new public surface (website, app, landing page, help centre, public status or marketing page, social
  profile); cookies, SDKs, pixels or analytics; a sign-up, checkout, plan term, renewal or cancellation flow;
  opening sign-up to individuals; prices on a page; terms text or a change to it; marketing claims, comparison
  pages, testimonials or a review widget; cold or warm outreach by email, phone or social messages, newsletters,
  lifecycle mails and review requests; consumer-facing UI that must be accessible; user content that others
  can see; data export, exit or egress fees; growth past 50 staff or EUR 10 million turnover; shipping an agent,
  CLI, SDK or app; adding an LLM or other AI feature; deleting accounts or business records. Also when someone
  asks whether the product is "legally compliant" or "rechtssicher".
- Does not apply: GDPR roles, AVV, VVT, TOM, DSFA, deletion and data-subject requests (`gdpr-engineering`);
  VAT, reverse charge, invoice content and e-invoice formats (`billing-eu-b2b`); plan limits
  (`plan-entitlements`); wording and tone of copy (`human-copy`, if installed); visual and accessibility
  practice (`design-quality`, if installed); law outside Germany and the EU; drafting a contract clause or
  answering a dispute, which goes to a lawyer.

## Rules

### Trigger table

Run this table on every plan and pull request that touches one of the surfaces above. Each hit names the law,
the baseline action and who takes it further. Detail and dates are in the references.

| The change | Law | Baseline action | Route |
|---|---|---|---|
| New public surface or social profile | DDG § 5 | Impressum one click away, same data everywhere | this skill; lawyer for journalistic content |
| Cookie, local storage, SDK, pixel, fingerprinting, analytics | TDDDG § 25 | consent, or a strictly-necessary reason per key | `gdpr-engineering` for legal basis and VVT |
| Sign-up open to individuals, or no business check | BGB §§ 13, 14, 312 ff. | ADR: B2B-only or consumers allowed | lawyer signs off the decision |
| Checkout, order button, renewal, cancellation, withdrawal | BGB §§ 312j, 312k, 355-357a, 356a, 309 Nr. 9 | consumer pack (see rules) | lawyer for texts |
| Prices shown to consumers | PAngV § 3 | total price incl. VAT | `billing-eu-b2b` for the rate |
| Terms text, new clause, terms change | BGB §§ 305-310 | versioned acceptance, change process | lawyer drafts |
| Claim, comparison page, testimonial, review widget | UWG §§ 5, 5b, 6, Anhang Nr. 23b, 23c | evidence per claim, review-check statement | lawyer for comparisons |
| Outreach by email, phone or social message; newsletter, lifecycle or review-request mail | UWG §§ 7, 7a | consent or § 7 Abs. 3 record per recipient, objection notice | `gdpr-engineering` for the dispatcher |
| Consumer-facing sign-up or checkout UI | BFSG §§ 1, 3, 14 | scope decision, accessible flow, accessibility info | `design-quality` |
| Users post content others can see | DSA Art. 11, 12, 14, 16-18 | contact points, notice and action, reasons | `gdpr-engineering` (ugc-dsa reference) |
| Export, exit, contract term, switching or egress fee | Data Act Art. 23-31 | switching terms, full export, fee phase-out | lawyer for contract terms |
| Headcount or turnover crosses a threshold; cloud or managed services | BSIG §§ 28, 32, 33 (NIS2) | scope check, registration, 24 h/72 h/1 month | lawyer for scope; incident runbook |
| Ships an agent, CLI, SDK, desktop or mobile app | CRA Art. 14, 71 | vulnerability reporting, product requirements | `release-supply-chain`, if installed |
| LLM chat, generated text, images or audio | AI Act Art. 4, 50, 113 | disclosure, marking, literacy, risk check | lawyer for role and risk class |
| Account deletion, retention job, purging records | AO § 147, HGB § 257, UStG § 14b | keep and restrict, do not delete | `gdpr-engineering` |
| Invoices to German businesses | UStG § 14, § 27 Abs. 38 | e-invoice timeline | `billing-eu-b2b` |
| "Are we compliant?" | all of the above | status per row, open items, who signs | lawyer, tax adviser |

### Rules

- [invariant] Never state that the product, a feature or a text is "compliant", "legally safe" or "rechtssicher".
  State the rule, its primary source and the date you read it, mark anything not read from a primary source as
  Unverified, and name who decides (lawyer, tax adviser, data protection officer). Label every legal draft
  "review-ready draft, not legal or tax advice". Why: an agent's certainty is not a legal opinion, and a team that
  hears "compliant" stops asking. Test: a reply or document produced under this skill contains no unqualified
  compliance verdict; every legal statement in it carries a source and date or the word Unverified; the PR
  description names the reviewing person. Source: authoring rule AR-14 of this repository; the statutes cited per
  row.
- [invariant] Run the trigger table on every plan or pull request that touches a listed surface. A hit gets its
  action or an issue owned by a person; no hit gets the line "legal: no change" with a reason. Why: legal work that
  the change does not trigger is done months later, after customers relied on the old state. Test: the pull request
  template has a legal section; a review that finds a touched surface (new route, cookie, plan term, AI call)
  without an entry fails. Source: this skill's table, verified 2026-11-03.
- [invariant] Every public surface reaches the Impressum in one click: website, app, help centre, public status and
  marketing pages, and commercial social profiles. The data (name, address, legal form and representatives, fast
  electronic contact including email, register and number, VAT ID if any) comes from one source. Why: DDG § 5
  requires the information to be "leicht erkennbar und unmittelbar erreichbar" and permanently available for
  business digital services, and copies drift. Test: a crawler visits every public route and app screen, follows the
  "Impressum" or "Legal notice" link and checks the required fields on a 200 response; a checklist row per social
  profile records the link. Source: DDG § 5 Abs. 1, https://www.gesetze-im-internet.de/ddg/__5.html (verified
  2026-11-03). Social profiles: treated as separate services in common practice, Unverified against a primary
  source.
- [default] Measure product usage with analytics that store and read nothing on the user's device, and put anything
  that needs a cookie, storage key or device identifier behind consent. Why: TDDDG § 25 makes consent the rule for
  device access and exempts only what is strictly necessary for a service the user asked for; analytics is not.
  Trade-off: no returning-visitor or cross-session metrics without consent. Deviate only with an ADR that names this
  trade-off. Test: a headless browser with no consent lists cookies, local and session storage and outgoing
  requests; only allowlisted keys exist and no analytics request carries an identifier read from the device. Source:
  TDDDG § 25 Abs. 1, 2, https://www.gesetze-im-internet.de/ttdsg/__25.html; EDPB Guidelines 2/2023 v2.0 (pixel and
  URL tracking can fall under Art. 5(3) ePrivacy),
  https://www.edpb.europa.eu/system/files/documents/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf
  (verified 2026-11-03).
- [invariant] Whether consumers may sign up is an explicit decision in an ADR, and code enforces it. B2B-only:
  sign-up records a business confirmation (wording version, timestamp, company name) server-side, and the decision
  how much proof to ask is the lawyer's. Consumers allowed: the consumer pack below ships first. Why: BGB §§ 13 and
  14 decide by the purpose of the contract, not by a form field, and an open sign-up with B2B-only terms invites
  consumer contracts without the consumer duties. Test: a sign-up request without the confirmation is rejected by
  the server (not only by the form); the account row stores the confirmation and the wording version.
  Source: BGB §§ 13 and 14, https://www.gesetze-im-internet.de/bgb/__13.html, https://www.gesetze-im-internet.de/bgb/__14.html
  (verified 2026-11-03).
- [invariant] When consumers can buy, the flow carries the statutory buttons, labelled as below or with equally
  unambiguous wording: an order button "zahlungspflichtig bestellen" (otherwise no contract), a Kündigungsbutton
  "Verträge hier kündigen" leading to a confirmation page with "jetzt kündigen", and, from 19 June 2026, a
  withdrawal function "Vertrag widerrufen" with "Widerruf bestätigen", each followed by a confirmation on a durable
  medium. Why: the statute sets the labels, and a missing cancellation button lets the consumer cancel at any time
  without notice. Test: an end-to-end test on a consumer account asserts the four labels, reaches the cancel and
  withdraw pages from every page without extra steps, and receives both confirmation emails with date and time.
  Source: BGB §§ 312j Abs. 3-4, 312k, 356a, https://www.gesetze-im-internet.de/bgb/__312k.html,
  https://www.gesetze-im-internet.de/bgb/__356a.html; date of application from Directive (EU) 2023/2673 Art. 2(1),
  https://eur-lex.europa.eu/eli/dir/2023/2673/oj (verified 2026-11-03).
- [invariant] Consumer subscriptions respect the term limits: initial term at most two years, automatic renewal only
  to an indefinite term cancellable at any time with at most one month's notice, notice before the first term ends
  at most one month. Prices shown to consumers are total prices including VAT. Why: longer terms in AGB are void,
  and a net price shown to consumers breaks PAngV. Test: plan configuration validation rejects a consumer plan whose
  term, renewal or notice values exceed these limits; a snapshot of the pricing page in consumer mode shows gross
  prices. Source: BGB § 309 Nr. 9, https://www.gesetze-im-internet.de/bgb/__309.html; PAngV § 3 Abs. 1,
  https://www.gesetze-im-internet.de/pangv_2022/__3.html (verified 2026-11-03).
- [invariant] AGB become part of a contract only through an active step at conclusion: a visible reference, a
  readable link and the customer's agreement, stored as (customer, document version, timestamp). Changes get a new
  version and either new agreement or a change process a lawyer approved; silence is never treated as agreement by
  default. Why: § 305 Abs. 2 sets the incorporation conditions for consumers, § 308 Nr. 4 and 5 limit change clauses
  and deemed consent, and in B2B § 307 still applies. Test: a paid action by an account that has not accepted the
  current version is blocked; the rendered terms come from the versioned source the acceptance points to. Source:
  BGB §§ 305, 305c, 307, 308, 310 Abs. 1, https://www.gesetze-im-internet.de/bgb/__305.html,
  https://www.gesetze-im-internet.de/bgb/__310.html (verified 2026-11-03).
- [invariant] Every factual marketing claim (numbers, "fastest", "only", "certified", "GDPR-compliant", uptime
  figures, customer counts) has an evidence entry with source and date; a comparison with a named competitor
  compares like with like on verifiable features or price, without disparaging. Why: UWG § 5 forbids misleading
  statements to consumers and to business buyers, and § 6 sets the conditions for comparative advertising. Test: a
  claims file maps each claim on public pages to evidence and a date; a CI check flags superlatives and figures on
  marketing pages without an entry. Source: UWG §§ 5, 6, https://www.gesetze-im-internet.de/uwg_2004/__5.html,
  https://www.gesetze-im-internet.de/uwg_2004/__6.html (verified 2026-11-03).
- [invariant] If the site shows customer reviews, it says whether and how they are checked to come from real
  customers, and it never buys, writes or selectively misrepresents them. Why: UWG § 5b Abs. 3 makes the
  verification information material, and Anhang Nr. 23b and 23c list unverified authenticity claims and fake reviews
  as always unfair. Test: the page with the review widget contains the verification statement; each stored review
  has a source and a verification field. Source: UWG § 5b Abs. 3 and Anhang,
  https://www.gesetze-im-internet.de/uwg_2004/__5b.html, https://www.gesetze-im-internet.de/uwg_2004/anhang.html
  (verified 2026-11-03).
- [invariant] Advertising to a recipient in Germany has a recorded basis before it is sent. Email, businesses
  included: prior express consent with a stored double opt-in, or all four conditions of § 7 Abs. 3. Calls:
  express consent from consumers (§ 7a: documented, kept five years), at least presumed consent from businesses.
  Every advertising message names the sender and a free way to object. Why: § 7 Abs. 2 has no B2B exception for
  email, and a review request or upsell line can make a mail advertising. Test: a send to a German address
  without a consent or § 7 Abs. 3 record is blocked; each advertising mail carries the objection link. Source:
  https://www.gesetze-im-internet.de/uwg_2004/__7.html, https://www.gesetze-im-internet.de/uwg_2004/__7a.html
  (verified 2026-11-03). Messenger and social messages: the reference; enforcement in code: `gdpr-engineering`.
- [invariant] Record a BFSG scope decision before consumers can sign up or buy online. E-commerce services to
  consumers are in scope since 28 June 2025; B2B-only services are not; micro-enterprises offering services (fewer
  than 10 staff and at most EUR 2 million turnover or balance sheet) are exempt. In scope means an accessible flow
  and published accessibility information. Why: the duty follows the customer group, so opening sign-up to consumers
  can bring it in without a code change. Test: the ADR states the scope with headcount and turnover; if in scope, an
  automated accessibility check runs on sign-up, checkout and cancellation in CI, a keyboard and screen-reader pass
  is recorded, and the accessibility information page returns 200. Source: BFSG § 1 Abs. 3 Nr. 5, § 2 Nr. 17 and 26,
  § 3 Abs. 3, § 14, https://www.gesetze-im-internet.de/bfsg/__1.html,
  https://www.gesetze-im-internet.de/bfsg/__3.html (verified 2026-11-03).
- [invariant] When users can post content that others see, add the DSA basics on top of the moderation flow in
  `gdpr-engineering`: a public single point of contact for authorities (with languages) and for users, moderation
  rules in the terms, a notice form, statements of reasons, and a path to report threats to life or safety to law
  enforcement. Why: Art. 11, 12, 14, 16, 17 and 18 apply to every hosting service regardless of size. Test: the
  contact page lists both points of contact and languages; a test notice creates a record and a receipt
  confirmation. Source: Regulation (EU) 2022/2065 Art. 11, 12, 14, 16-18, 93,
  https://eur-lex.europa.eu/eli/reg/2022/2065/oj (verified 2026-11-03).
- [invariant] A SaaS that is a data processing service under the Data Act offers switching: contract terms with at
  most two months' notice, a transitional period of 30 days, at least 30 days to retrieve data, an exhaustive list
  of exportable data, erasure afterwards, and no switching charges from 12 January 2027 (until then at most the
  direct cost, disclosed before contract). Why: Chapter VI (switching) has applied since 12 September 2025 without a
  separate date for older contracts, and a multi-tenant SaaS sold from a catalogue does not fall under the
  custom-built exemption. Test: a full tenant export completes and re-imports in a test; billing has no switching or
  egress-fee line dated from 12 January 2027; the terms checklist ticks each Art. 25 item. Source: Regulation (EU)
  2023/2854 Art. 25, 29, 31, 50, https://eur-lex.europa.eu/eli/reg/2023/2854/oj (verified 2026-11-03). Pending
  amendments for SMEs and custom services: Unverified, not adopted as of this date per secondary sources.
- [invariant] Review NIS2 scope at least yearly and whenever headcount or turnover crosses a threshold or the
  product adds cloud computing or managed services: an important entity has at least 50 staff or more than EUR 10
  million turnover and balance sheet; registration with the BSI is due within three months; significant incidents
  are reported within 24 hours, 72 hours and one month. Why: the German act has been in force since 6 December 2025
  without a general transition period, and the deadlines run from the day the threshold is crossed. Test: the ADR
  log has a dated scope entry with the figures; the incident runbook contains the three reporting clocks and the
  reporting channel. Source: BSIG §§ 28, 32, 33 and Anlage 1 Nr. 6.1.4, 6.1.10,
  https://www.gesetze-im-internet.de/bsig_2025/__28.html; BSI press release of 5 December 2025,
  https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2025/251205_NIS-2-Umsetzungsgesetz_in_Kraft.html
  (verified 2026-11-03). Whether a given SaaS is a "cloud computing service": lawyer.
- [invariant] Shipping software to customers (an agent, CLI, SDK, desktop or mobile app) makes you a manufacturer
  under the Cyber Resilience Act, and the backend that software needs is in scope as remote data processing; a
  web-only SaaS is not. Actively exploited vulnerabilities and severe incidents are reported from 11 September 2026
  (24 hours, 72 hours, final report); the rest applies from 11 December 2027. Why: the reporting duty already
  applies to products on the market, before the product requirements do. Test: the release inventory lists every
  artifact shipped to customers; the security runbook has the CRA reporting clocks and the reporting platform;
  releases carry an SBOM. Source: Regulation (EU) 2024/2847 Art. 14, 71, Recital 12,
  https://eur-lex.europa.eu/eli/reg/2024/2847/oj (verified 2026-11-03).
- [invariant] An AI feature tells people they are interacting with an AI system unless it is obvious, marks
  generated audio, image, video or text as machine-readable where you are the provider, discloses deepfakes, and is
  logged in an AI register with your role (provider or deployer) and a risk check against prohibited and high-risk
  uses. Art. 50 applies from 2 August 2026; systems on the market before that date have until 2 December 2026 for
  marking. Why: the transparency duties apply to small companies too, and high-risk uses (for example hiring or
  credit decisions) change the whole regime. Test: a UI test asserts the AI notice on first interaction; generated
  files carry provenance metadata; the register has one row per AI feature. Source: Regulation (EU) 2024/1689 Art.
  4, 50, 113, https://eur-lex.europa.eu/eli/reg/2024/1689/oj; Regulation (EU) 2026/1744 (Digital Omnibus on AI),
  https://eur-lex.europa.eu/eli/reg/2026/1744/oj (verified 2026-11-03).
- [invariant] Records with a tax or commercial retention duty are kept and restricted, not deleted, when an account
  is erased. Since 1 January 2025 invoices and booking vouchers are kept eight years (previously ten), books and
  annual accounts ten, business letters six, each from the end of the calendar year; banks, insurers and investment
  firms keep ten for vouchers. Why: the shorter period applies to all records not yet expired on 31 December 2024,
  so a purge job still on ten years keeps data without a basis, and one on six deletes too early. Test: an invoice
  and a voucher survive account erasure with personal fields not needed for the duty cleared and access restricted;
  `retain_until` matches the rule for a 2026 invoice (deletable from 1 January 2035). Source: AO § 147 Abs. 3-4,
  https://www.gesetze-im-internet.de/ao_1977/__147.html; EGAO Art. 97 § 19a,
  https://www.gesetze-im-internet.de/aoeg_1977/art_97__19a.html; UStG § 14b, § 27 Abs. 40,
  https://www.gesetze-im-internet.de/ustg_1980/__14b.html; HGB § 257 Abs. 4,
  https://www.gesetze-im-internet.de/hgb/__257.html (verified 2026-11-03). Deletion mechanics: `gdpr-engineering`.
- [default] Keep a legal register in the repository: one row per trigger-table law with in scope yes or no, the
  decision, its source and date, the owner and the next review date. Why: scope answers change with headcount,
  customer group and product, and nobody remembers why "not in scope" was true. Trade-off: a file that needs a
  yearly review. Deviate only with an ADR that names this trade-off. Test: a scheduled CI job fails when a row's
  review date has passed. Source: the dated rows in this skill, verified 2026-11-03.

## Procedure

1. Gate: run the trigger table. No hit: write "legal: no change" and the reason, and stop.
2. For each hit, read the matching reference and the primary source it names. Re-check dates that lie within a
   year of today; regulations in this area are amended often.
3. Decide what the code can enforce (buttons, labels, storage allowlist, exports, retention dates, registers) and
   write the tests the rules name.
4. Draft the texts the hit needs (Impressum data, terms clause, accessibility information, AI notice) as
   review-ready drafts and hand them to the person who signs. Publishing a legal text or sending notices to
   customers is an external action: follow `safe-actions`.
5. Update the legal register with the decision, the source and the date.

### Pre-launch legal checklist

Each item is answered with yes, no or not applicable, a source and a date. "Not sure" goes to the lawyer.

- [ ] Impressum reachable in one click from site, app, help centre, public pages and every social profile.
- [ ] Privacy notice, AVV and subprocessor list current (`gdpr-engineering`).
- [ ] Before consent, the browser stores only allowlisted keys; consent banner tested.
- [ ] ADR: B2B-only or consumers allowed; sign-up enforces it server-side.
- [ ] If consumers: Widerrufsbelehrung, order button, Kündigungsbutton, withdrawal function, gross prices, term
      limits, confirmation emails; BFSG scope decided.
- [ ] AGB and privacy texts versioned; acceptance stored; change process approved by the lawyer.
- [ ] Every claim on marketing pages has evidence; comparison pages reviewed; review widget states verification.
- [ ] Outreach and advertising mail: consent or § 7 Abs. 3 record per recipient, double opt-in stored, objection
      link in every mail, no cold email or unconsented calls to German recipients.
- [ ] User content: contact points, notice form, statements of reasons, moderation rules in the terms.
- [ ] Data Act: switching clauses, full export, no switching charges after 12 January 2027.
- [ ] NIS2 scope entry dated; incident runbook has the 24 h / 72 h / 1 month clocks.
- [ ] Shipped software listed; CRA reporting path ready.
- [ ] AI features in the register with notice, marking and risk check.
- [ ] Retention periods in purge jobs match the 2025 rules; invoices and vouchers survive erasure.
- [ ] Invoice output plan meets the e-invoice dates (`billing-eu-b2b`).
- [ ] Lawyer and tax adviser named for each open item, with a date.

## Traps

- "We are B2B" written only in the terms. Without a sign-up check, consumers sign up anyway, and the consumer
  duties attach to their contracts.
- An Impressum page that exists but is linked only from the marketing site; the app, the help centre and social
  profiles have none.
- "Cookieless" analytics that still uses local storage, a fingerprint or a tracking pixel. Test what the browser
  does, not what the vendor page says.
- A cancellation flow behind three menus and a retention offer. The statute wants the button reachable and the
  confirmation page direct.
- Copying the old ten-year retention from an earlier policy; since 2025 invoices and vouchers are eight years.
- Treating the AI Act as a high-risk-only law. A chat assistant in a project tool already has Art. 50 duties.
- A "GDPR-compliant" badge on the landing page with no evidence behind it is a marketing claim under UWG § 5.

## Done when

- The plan or pull request answers the trigger table: each hit with its action and owner, or "no change" with a
  reason.
- The tests named by the triggered rules exist and pass.
- Drafted legal texts carry the review-ready label, dated sources and the name of the person who signs.
- The legal register rows for the touched laws carry today's date.

## References

- [references/notices-terms-marketing-de.md](references/notices-terms-marketing-de.md): load for Impressum,
  cookies and analytics, AGB incorporation and changes, marketing claims, comparisons, reviews and outreach.
- [references/consumer-sales-de.md](references/consumer-sales-de.md): load when consumers can sign up or buy,
  or when deciding B2B-only.
- [references/accessibility-bfsg.md](references/accessibility-bfsg.md): load when deciding BFSG scope or
  building consumer-facing flows.
- [references/eu-digital-regulations.md](references/eu-digital-regulations.md): load for DSA, Data Act, NIS2
  and BSIG, CRA and AI Act duties and dates.
- [references/retention-de.md](references/retention-de.md): load when a purge job, account erasure or retention
  setting touches business records.
- [references/verification-status.md](references/verification-status.md): load before citing any fact from
  this skill, to see what was verified on which source and what is Unverified.

## Sources

All verified 2026-11-03; per-fact status in [references/verification-status.md](references/verification-status.md).

- German statutes, https://www.gesetze-im-internet.de/: DDG § 5; TDDDG § 25; BGB §§ 13, 14, 305, 305c, 308, 309,
  310, 312g, 312j, 312k, 355, 356, 356a, 357a; PAngV § 3; UWG §§ 5, 5b, 6, 7, 7a and Anhang; BFSG §§ 1, 2, 3, 14,
  38; BSIG §§ 28, 32, 33, Anlage 1; AO § 147, HGB § 257, UStG §§ 14b, 27.
- https://www.edpb.europa.eu/system/files/documents/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf:
  EDPB Guidelines 2/2023 v2.0.
- EU law, https://eur-lex.europa.eu/: Directive 2023/2673 (withdrawal function from 19 June 2026), DSA 2022/2065,
  Data Act 2023/2854, NIS2 2022/2555 Art. 23, CRA 2024/2847, AI Act 2024/1689 and Digital Omnibus 2026/1744.
