# Go-to-market plan: [product], [segment]

created: [YYYY-MM-DD]
Owner: [name or role]
Skills: go-to-market

Copy this file to `docs/marketing/gtm-plan.md`, replace every `[...]`, then run `check_gtm_plan.py` on it.
Numbers are plain digits in the currency named under Inputs, net, without a thousands separator (`1200`, not
`1.200`). Dates are `YYYY-MM-DD`.

## Inputs

| Input | Value | Source |
|---|---|---|
| Product brief | docs/product/brief.md | product-strategy |
| Pricing model | docs/product/pricing.md | pricing-and-unit-economics |
| Currency | EUR | pricing model |
| Contract value per year | [net amount one typical paying customer pays per year, for example 1200] | pricing model |
| Gross margin percent | [for example 80] | pricing model |
| Payback target months | [for example 12] | pricing model or owner decision |

Ceiling for the cost to win one paying customer, computed by the checker:
contract value per year x gross margin percent / 100 x payback target months / 12.
Example: 1200 x 0.80 x 12 / 12 = 960. No channel and no sales motion may plan above it.

## Sales motion

| Field | Value |
|---|---|
| Motion | [self-serve, inside or field] |
| Sales cost per won deal | [sales and demo hours per won deal x cost per hour, 0 for self-serve] |
| Founder-led until | [YYYY-MM-DD or a count of won deals, for example "first 20 paying customers"] |
| Reason | [the numbers that chose the motion: contract value band, sales cost, payback] |

Bands by contract value per year (practice, Janz 2014, see the skill's sales-motions reference): below 10000
self-serve, 10000 to 99999 inside sales, 100000 and above field sales.

## Channels

Statuses: planned, running, proven (met its cost target over the read window), stopped.

| # | Channel | Evidence buyer is there | Target cost per paying customer | Attribution field | Start date | Read date | Stop/scale rule | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | [channel, for example an app marketplace listing] | [for example 4 of 10 interviewed customers found tools there] | [number at or below the ceiling] | [field stored on the account, for example signup_source=marketplace] | [YYYY-MM-DD] | [YYYY-MM-DD, at least 28 days after start] | [with numbers, for example stop if above 960 per paying customer after 2 monthly cohorts; scale if below 600] | planned |

## Outreach and mail

One row per message kind and country. Channels: email, sms, messenger, social-message (LinkedIn, Xing and
similar), phone, automated-call, fax, letter. Types: transactional, advertising. Legal basis: consent,
§ 7 Abs. 3, presumed B2B phone, n/a. Review-ready draft, not legal advice; Germany only, other countries need
their own check (`eu-de-legal-baseline`).

| # | Message | Channel | Recipients from | Country | Type | Legal basis | Proof stored where |
|---|---|---|---|---|---|---|---|
| 1 | [sign-up confirmation] | email | [own sign-up form] | DE | transactional | n/a | n/a |
| 2 | [newsletter] | email | [double opt-in form on the site] | DE | advertising | consent | [where the opt-in records live, for example the consents table] |
| 3 | [win-back to former customers] | email | [own customers' order data] | DE | advertising | § 7 Abs. 3 | [record of the notice given at collection and in every mail] |

## Launch checklist

Launch date: [not set, or YYYY-MM-DD once every box below is ticked]

- [ ] Positioning and price stored; launch message checked against the product-truth table.
- [ ] A new account reaches its first result without help; tested on a fresh account.
- [ ] Attribution on every launch link; the sign-up source stored on the account.
- [ ] Directory and marketplace profiles complete and current.
- [ ] Owned audience contacted only with consent or under § 7 Abs. 3 UWG.
- [ ] Support capacity and a known-issues note for launch day.
- [ ] Changelog and docs updated; pages for new features live and indexed.
- [ ] A read date and the metrics to report: attributed sign-ups, paying customers, cost per paying customer.

## Owners

| Area | Owner |
|---|---|
| Plan and budget | [name or role] |
| Channels | [name or role] |
| Outreach and mail, approves every send | [name or role] |
| Legal review | [name or role, or eu-de-legal-baseline plus counsel] |
| Attribution and the read-date report | [name or role] |
