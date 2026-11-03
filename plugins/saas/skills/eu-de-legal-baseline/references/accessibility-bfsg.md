# Accessibility duties (BFSG)

Review-ready draft, not legal advice. Scope: Germany, implementing the European Accessibility Act (Directive
(EU) 2019/882). Statute text read on gesetze-im-internet.de on 2026-11-03.

## Scope decision

- The Barrierefreiheitsstärkungsgesetz (BFSG) covers services provided to consumers after 28 June 2025 (§ 1
  Abs. 3). For a SaaS the relevant entry is Nr. 5, "Dienstleistungen im elektronischen Geschäftsverkehr":
  digital services offered through websites and mobile apps, provided electronically on a consumer's individual
  request with a view to concluding a consumer contract (§ 2 Nr. 26).
- A B2B-only service is outside that definition, because the definition requires a consumer contract.
- Micro-enterprises that offer services are exempt from the accessibility requirements (§ 3 Abs. 3):
  fewer than ten employees and either annual turnover or balance sheet total of at most EUR 2 million (§ 2
  Nr. 17).
- Transitional rules (§ 38): services may keep using products they lawfully used before 28 June 2025 until 27
  June 2030 at the latest, and contracts concluded before that date may continue unchanged until they end, at
  the latest 27 June 2030.
- Third-party content the operator neither funds, develops nor controls, and archived content not updated
  after 28 June 2025, are excluded (§ 1 Abs. 4).

Record the decision in an ADR with headcount, turnover, the customer groups that can sign up and the date.
Re-check it when sign-up opens to consumers or the company passes the micro-enterprise limits.

## When in scope

- Requirements: set by the BFSGV regulation based on Annex I of Directive (EU) 2019/882 (§ 3 Abs. 2). Which
  technical standard gives a presumption of conformity was not checked here (Unverified); ask the lawyer or the
  market surveillance guidance before relying on a WCAG level.
- Publish the information Anlage 3 requires, in accessible form, for as long as the service is offered (§ 14).
  The exact contents of Anlage 3 were not re-read here (Unverified).
- Cover the whole consumer journey: landing page, sign-up, login, checkout, payment, account settings, the
  Kündigungsbutton and withdrawal function, emails and PDFs the flow sends.

## Engineering practice

- Visual and interaction practice (contrast, focus states, keyboard paths, form errors) is in `design-quality`
  if installed. This file only decides whether the law applies.
- CI: an automated accessibility checker on the consumer flows, failing on new violations.
- Manual: a keyboard-only pass and a screen-reader pass per release of the consumer flows, recorded with date
  and tester.
- An automated checker finds only part of the problems. A green CI run is not a statement that the flow meets
  the BFSG.
