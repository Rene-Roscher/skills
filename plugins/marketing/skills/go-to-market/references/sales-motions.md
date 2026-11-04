# Sales motions

The motion follows from what a won deal is worth and what it costs to win it. Take contract value, gross
margin and payback target from the pricing model (`pricing-and-unit-economics`) and compute the ceiling:

ceiling per paying customer = contract value per year x gross margin percent / 100 x payback months / 12

Everything spent to win one paying customer (sales hours, demos, ads, listings) fits under the ceiling. The
bands below are a starting point from public practice; when they disagree with the ceiling, the ceiling wins.

## Decision table

Practice, not a rule. Bands from Christoph Janz, "Five ways to build a $100 million business", 5 October 2014,
https://christophjanz.blogspot.com/2014/10/five-ways-to-build-100-million-business.html (verified 2026-11-04).
Janz states average revenue per account per year in US dollars; the plan uses the same thresholds in its own
currency.

| Contract value per year (net) | Janz's name | Motion | What Janz names as the way to win them |
|---|---|---|---|
| below 1000 | mice (100+ per year) | self-serve | some level of virality |
| 1000 to 9999 | rabbits (1k+ per year) | self-serve | inbound marketing, a product with high NPS, funnel optimisation |
| 10000 to 99999 | deer (10k+ per year) | inside sales | the rabbit playbook plus an inside sales force to close leads |
| 100000 and above | elephants (100k+ per year) | field sales | a founder team with enterprise sales skills |

Janz's fifth band, flies (10+ per year, ad-supported consumers), does not apply to B2B SaaS.

## Payback

Practice, from David Skok, "SaaS Metrics 2.0", https://www.forentrepreneurs.com/saas-metrics-2/ (verified
2026-11-04; the page shows no publication date): many of the best SaaS businesses recover their customer
acquisition cost in 5 to 7 months, profitability is "anemic" beyond 12 months, and the best have a lifetime
value to acquisition cost ratio above 3. Skok's worked example uses revenue (500 per month x 12 = 6000); the
ceiling above also multiplies by gross margin, which is stricter and is this skill's choice.

Worked example, project tool at 100 per month net: contract value 1200, gross margin 80, payback 12 gives a
ceiling of 960. A 45-minute demo plus 2 hours of onboarding at 60 per hour (165) fits; 10 hours of sales time
at 100 per hour (1000) does not, so the motion is self-serve with an optional call.

## What each motion requires

| Motion | Fits when the deal pays for | What it requires |
|---|---|---|
| Self-serve | no human time per deal | sign-up without a call, a first result within the first session, prices on the site, card or invoice checkout, help docs, in-product and lifecycle onboarding, support by ticket |
| Inside sales | a few hours per deal | a demo or assisted trial path next to self-serve, a CRM with stages, a sales deck and objection notes from real calls, security and data-protection answers ready (AVV, subprocessors), quotes and invoicing without card |
| Field sales | weeks of several people per deal | named accounts, procurement and security questionnaires, contract negotiation with a lawyer, pilots with success criteria, reference customers who agreed to be named |

## Founder-led sales

- Before any hire, the founder runs the first deals: discovery calls, demos, onboarding by hand. The output is
  the objection list, the buyer's words for the problem and the steps where trials stall.
- Write those down (`product-strategy` keeps the buyer and alternatives; this skill keeps objections and the
  sales steps). The plan's "Founder-led until" field names when this phase ends, as a date or a count of won
  deals.
- Hire sales when the founder's calendar is the limit and the motion's cost per won deal is known and under the
  ceiling.

## Mixed motions

- Self-serve plus a "talk to us" path for larger accounts is common. Keep one price list; quotes for larger
  accounts follow the same plan limits.
- A demo gate in front of a product that self-serve buyers could try alone loses them. Offer the trial, and the
  call as an option.

## Signals the motion is wrong

- Trials that stall at the same setup step: onboarding problem, not a sales problem.
- Deals that need security reviews on a self-serve price: either a higher plan with the review included, or
  decline the review.
- Sales cost per won deal above the ceiling (checker G08): move down a motion or raise the price
  (`pricing-and-unit-economics`).
