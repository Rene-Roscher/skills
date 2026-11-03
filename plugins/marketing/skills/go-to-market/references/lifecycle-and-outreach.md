# Lifecycle mail and outreach

Review-ready draft, not legal advice. Scope: Germany for the legal lines; other countries need their own check.
Statutes read on 2026-11-03.

## Mail types

| Type | Examples | Legal basis for sending (Germany) |
|---|---|---|
| Transactional | sign-up confirmation, password reset, invoice, receipt, security notice, alert the customer configured | the contract; no advertising content inside |
| Advertising | newsletter, upsell, plan upgrade offer, win-back, review request, event invitation, most "how is it going" nudges | prior express consent, or all four conditions of § 7 Abs. 3 UWG |
| Unclear | onboarding tips on how to use what the customer bought | decide with counsel, record the decision |

§ 7 Abs. 3 UWG (existing customers), all four needed:

1. the address came from the customer in connection with a sale of goods or a service,
2. it is used for direct advertising of your own similar goods or services,
3. the customer has not objected,
4. the customer was told clearly at collection and is told in every mail that they can object at any time at no
   cost beyond basic transmission rates.

Source: https://www.gesetze-im-internet.de/uwg_2004/__7.html (verified 2026-11-03).

## Lifecycle plan

| Stage | Trigger (product event) | Goal metric |
|---|---|---|
| Activation | account created, key setup step not done after a set time | share reaching first result |
| Conversion | trial or free plan near a limit or end date | share converting to paid |
| Expansion | usage near a plan limit | upgrades |
| Win-back | cancelled, after a set time | re-subscriptions |

- One goal per mail; the link goes to the step, not the home page.
- Read the step's conversion for a cohort, not open rates (open tracking is unreliable and needs a VVT entry).
- Transactional mails stay free of upsell lines.
- Contact data collected for operational alerts is never used for advertising (`gdpr-engineering`).

## Outreach in Germany (§ 7 Abs. 2 UWG)

| Channel | Consumers | Businesses |
|---|---|---|
| Email | prior express consent | prior express consent; no B2B exception |
| Phone call | prior express consent, documented and kept five years (§ 7a) | at least presumed consent; what counts as enough reason is case law, ask counsel |
| Automated calls, fax | prior express consent | prior express consent |
| SMS, LinkedIn, Xing, messenger messages | treat as email | treat as email; Unverified against a primary source |
| Letter by post | not when recognisably unwanted (§ 7 Abs. 1), for example after an objection | same |

Every advertising message: sender identity not hidden, a valid address for objections at no extra cost.

Sources: https://www.gesetze-im-internet.de/uwg_2004/__7.html,
https://www.gesetze-im-internet.de/uwg_2004/__7a.html (verified 2026-11-03).

## Proving consent

- Double opt-in: sign-up form, then a confirmation mail with a link; store address, timestamp of both steps,
  IP, the consent text version and the source form. The confirmation mail contains no advertising.
- The sender bears the burden of proving consent; a confirmed double opt-in is accepted as a way to document
  it (BGH I ZR 164/09, read from secondary sources; the case concerned phone advertising).
- Every advertising mail carries an unsubscribe link and a `List-Unsubscribe` header; an objection takes effect
  at once for all advertising.

## Alternatives when cold email is not allowed

- Inbound: comparison and problem pages, integrations, marketplaces, webinars with registration consent.
- Warm introductions from customers and partners, with the introducer's mail.
- Events and communities where the buyer is present.
- Business phone calls only with a documented reason for presumed consent, reviewed by counsel first.
