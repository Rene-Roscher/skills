---
name: go-to-market
description: "Plans how a B2B SaaS finds and wins paying customers: sales motion by contract value, channel choice and proof, launches, directories and review platforms, lifecycle mail, outreach legality, referrals and partners, each judged by cost per paying customer. Use when planning a launch, channel, campaign, lifecycle mails, cold outreach or review requests. Not for SEO pages, prices or positioning."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Go-to-market

This skill decides how a B2B SaaS reaches buyers and turns them into paying customers: which sales motion the
contract value can carry, which channel to prove first, how a launch is prepared, which mails the product sends
after sign-up, how outreach stays legal, and how reviews, referrals and partners work. Every plan names a cost
per paying customer and is judged on attributed revenue from `search-measurement`, not on traffic. Positioning
comes from `product-strategy`, prices from `pricing-and-unit-economics`, pages from `search-visibility`, wording
from `human-copy`, law from `eu-de-legal-baseline`. The failure it prevents: activity that looks like marketing
(posts, upvotes, cold sequences, ten channels at once) with no paying customer traced to it, or one that breaks
German outreach law.

## Fast path

1. Copy [assets/gtm-plan-template.md](assets/gtm-plan-template.md) to `docs/marketing/gtm-plan.md` and replace
   every `[...]` with a value from the product brief, the pricing model or the owner.
2. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_gtm_plan.py docs/marketing/gtm-plan.md`.
3. Exit 1 or 2: stop. Fix each error, or report it to the owner with its ID; nothing is spent, sent or posted
   on that plan. An error naming `product-strategy` or `pricing-and-unit-economics` means: run that skill first.
4. Exit 0: explain each remaining warning in the plan, then show the plan to the owner.
5. Sending mail, posting, submitting a listing or contacting anyone waits for the owner's go (`safe-actions`).
6. Positioning, price, budget and legal grey areas (any G26 or G27 warning, any mail that is neither clearly
   transactional nor clearly advertising) are the owner's call: list them, do not decide them.

## Applies when / does not apply

- Applies: a launch or relaunch; choosing or reviewing a channel; a campaign; onboarding, trial, conversion or
  win-back mails; cold email, calls or LinkedIn messages; review requests and review platforms; directory
  listings; referral, affiliate, partner or reseller programmes; "how do we get customers", "should we hire
  sales", "do we need demos".
- Does not apply: who the buyer is and positioning (`product-strategy`); prices, plans, trial versus freemium
  economics (`pricing-and-unit-economics`); competitor facts (`market-analysis`); SEO and comparison pages
  (`search-visibility`); measurement, snapshots and attribution data (`search-measurement`); wording
  (`human-copy`); the mail dispatcher and consent records in code (`gdpr-engineering`).

## Rules

- [invariant] Positioning and price come first. A launch, campaign or channel plan starts from the stored
  `product-strategy` output (buyer, alternatives, positioning) and a price from `pricing-and-unit-economics`;
  if either is missing, run that skill before this one. Why: messages without a named buyer and alternative are
  generic, and a channel cannot be judged without knowing what a customer is worth. Test: "plan our launch" in
  a repository without `docs/product/` produces a stop that names the missing inputs, not a launch plan;
  `check_gtm_plan.py` reports G03 or G04 with the skill to run. Source: this repository's `product-strategy` and `pricing-and-unit-economics` skills.
- [invariant] Every channel, launch and campaign has a target cost per paying customer, derived from the payback
  target in the pricing model, and is judged on sign-ups attributed to it that became paying, read from
  `search-measurement`. Visits, impressions, followers, upvotes and open rates are inputs. Why: B2B traffic and
  revenue diverge, and a channel that brings sign-ups who never pay costs money twice. Test: a report with
  visits and upvotes only is incomplete; a complete one lists spend, attributed sign-ups, paying customers and
  cost per paying customer per channel for a stated window; the checker reports G12 or G13 for a channel
  without a numeric target or above the ceiling (contract value x gross margin x payback months / 12), and G14
  without an attribution field. Source: this repository's `search-measurement` attribution rule.
- [default] Choose the sales motion from contract value: self-serve when the annual contract value cannot pay
  for a salesperson's time, inside sales (demo, assisted trial, short calls) when it pays for a few hours per
  deal, field sales only when it pays for long cycles with several stakeholders. Starting bands, practice from
  Janz 2014 (verified 2026-11-04): contract value per year below 10000 self-serve, 10000 to 99999 inside sales,
  100000 and above field sales. The sales cost per won deal stays under the ceiling; when band and ceiling
  disagree, the ceiling wins. Early on, the founder sells and onboards by hand to learn objections. Trade-off:
  self-serve gives up the deals that need a conversation. Deviate only with an ADR that names this trade-off.
  Test: the checker reports G08 for a sales cost above the ceiling and warns G09 when the motion is outside the
  band. Source: https://christophjanz.blogspot.com/2014/10/five-ways-to-build-100-million-business.html
  (verified 2026-11-04). Detail: [references/sales-motions.md](references/sales-motions.md).
- [default] Pick channels from where the buyer already looks (interview notes, the sign-up "how did you hear
  about us" field, search demand, communities the buyer reads) and run one channel until it meets its cost
  target over cohorts set in advance, before adding the next. Trade-off: slower reach while one channel is
  proven. Deviate only with an ADR that names this trade-off. Test: the checker reports G11 without evidence,
  G16 for a stop/scale rule without a number, and warns G18 when more than one unproven channel starts within
  30 days.
- [invariant] Outreach is checked against the recipient's country before anything is sent. In Germany,
  advertising by email needs the addressee's prior express consent, businesses included; advertising calls need
  express consent from consumers (documented, kept five years) and at least presumed consent from businesses;
  every advertising message names the sender and gives a free way to object. Treat LinkedIn and messenger
  messages like email (Unverified). Route to `eu-de-legal-baseline`. Why: § 7 UWG presumes these contacts an
  unreasonable nuisance, and competitors enforce it. Test: "send a cold email campaign to these German
  companies" gets no sequence for those recipients, the statutory reason, and consent-based alternatives; the
  checker reports G23 for advertising email to DE without consent or § 7 Abs. 3 and G25 for a cold or bought
  list. Source: https://www.gesetze-im-internet.de/uwg_2004/__7.html,
  https://www.gesetze-im-internet.de/uwg_2004/__7a.html (verified 2026-11-03). Review-ready draft, not legal
  advice.
- [invariant] Each lifecycle mail is classed transactional or advertising before it is written. Advertising
  (newsletter, upsell, win-back, review request, most activation nudges) needs consent or all four conditions of
  § 7 Abs. 3 UWG, and carries the objection notice in every mail; transactional mail carries no advertising.
  Enforcement in code: `gdpr-engineering`. Why: a review or upsell line inside an invoice mail can make it
  advertising (BGH VI ZR 225/17, read from secondary sources only). Test: the outreach and mail table has
  columns type and legal basis; a win-back mail to former customers without a consent or § 7 Abs. 3 record is
  blocked (checker G22, G24).
  Source: https://www.gesetze-im-internet.de/uwg_2004/__7.html (verified 2026-11-03).
- [default] Lifecycle mails are triggered by product events (setup step missing, first result reached, trial
  ending, usage dropped), have one goal each, and are judged on that step's conversion, not on opens. Trade-off:
  needs event tracking in the product before the mails. Deviate only with an ADR that names this trade-off.
  Test: each mail in the plan names its event, its goal metric and the window it is read in.
- [invariant] Review requests go to every customer the same way, never only the happy ones; incentives only
  where the platform allows them and never tied to the rating; no review is written, bought or commissioned.
  Trustpilot and Google forbid incentives; G2 runs its own rating-independent incentive campaigns. Why: gating
  and incentives get reviews removed, and fake reviews are always unfair under UWG Anhang Nr. 23c. Test: a
  "send the review link only to NPS 9-10" plan is refused with the platform rules. Source:
  https://corporate.trustpilot.com/legal/for-everyone/action-we-take,
  https://support.google.com/contributionpolicy/answer/7400114, https://legal.g2.com/community-guidelines,
  https://www.gesetze-im-internet.de/uwg_2004/anhang.html (verified 2026-11-03).
- [invariant] Directory, marketplace and review-platform profiles, decks and campaign copy state only what
  ships: features, limits and prices read from config, the same product description everywhere, updated when
  the product changes. No invented customer counts, logos or testimonials. Why: assistants and buyers repeat
  third-party profiles, and UWG § 5 covers business buyers. Test: each profile has a row in a profiles list
  with its last check date and a diff against current config. Source:
  https://www.gesetze-im-internet.de/uwg_2004/__5.html (verified 2026-11-03).
- [default] A launch is prepared, then timed: onboarding works end to end for a new account, attribution is
  live, directory profiles are complete, support can answer, and the owned audience (with consent) hears first.
  Use one launch moment only for news that a buyer would act on; otherwise ship and announce continuously.
  Trade-off: a single moment concentrates attention and risk on one day. Deviate only with an ADR that names
  this trade-off. Test: the checker reports G28 when the plan sets a launch date while a
  checklist box is open; detail in [references/channels-and-launch.md](references/channels-and-launch.md).
- [default] Referral rewards pay on a paying customer after the refund or withdrawal window, not on sign-up;
  partner and reseller terms are written, with margin taken from the pricing model; partner and affiliate
  content discloses the commercial relationship. Trade-off: slower payouts make the programme less attractive.
  Deviate only with an ADR that names this trade-off. Source:
  https://www.gesetze-im-internet.de/uwg_2004/__5a.html (Abs. 4) (verified 2026-11-03).

## Procedure

1. Load the product brief and the pricing model. Missing: stop and route (first rule).
2. Copy [assets/gtm-plan-template.md](assets/gtm-plan-template.md) to `docs/marketing/gtm-plan.md` (or the
   project's marketing docs) and fill it: inputs, motion with its numbers, channels with evidence and cost
   targets, outreach and mail with country and legal basis, launch checklist, owners.
3. Check every outreach and mail row against [references/lifecycle-and-outreach.md](references/lifecycle-and-outreach.md)
   and route open questions to `eu-de-legal-baseline`.
4. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_gtm_plan.py docs/marketing/gtm-plan.md`. In clients that
   don't set `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder; `--root` is the repository
   root when run from elsewhere. Exit 1: fix every error or report it. Exit 2: the checker did not run; fix the
   call. Explain each remaining warning in the plan.
5. Ask `search-measurement` to set up attribution and log each start date.
6. Sending mail, posting, submitting to directories or contacting people are external actions: draft, show,
   and act only on the owner's go (`safe-actions`).
7. At the read date, rerun the checker (G19 lists channels due), report per channel with the numbers from the
   second rule, and set stop, keep or scale.

## Traps

- Copying US practice: cold email sequences and "just add them to the newsletter" are not legal for German
  recipients.
- A single "launch day" with no attribution: hundreds of visits, no idea which brought a paying account.
- Five channels started at once, none run long enough to judge.
- Win-back mails to churned customers whose address was collected only for operational alerts.
- Partner directories and old review profiles still describing last year's product and prices.
- Demo-only sign-up on a product whose price cannot pay for the demo.

## Done when

- `check_gtm_plan.py` exits 0 on the plan, and each remaining warning is explained in it.
- The plan names buyer, motion, channels with evidence, cost per paying customer targets and read dates.
- Every outreach channel and mail has a legal basis entry or is removed.
- Attribution is live before the first euro or hour is spent, and results are reported as paying customers.

## References

- [assets/gtm-plan-template.md](assets/gtm-plan-template.md): copy to `docs/marketing/gtm-plan.md` for every
  plan; its sections and tables are what the checker reads.
- `${CLAUDE_SKILL_DIR}/scripts/check_gtm_plan.py`: run before acting on a plan and at each read date. `--help`
  lists the checks G01 to G29; `--self-test` runs its fixtures.
- [references/sales-motions.md](references/sales-motions.md): load when choosing self-serve, inside or field
  sales, or founder-led selling.
- [references/channels-and-launch.md](references/channels-and-launch.md): load for channel choice, launch
  preparation, directories and review platforms.
- [references/lifecycle-and-outreach.md](references/lifecycle-and-outreach.md): load for lifecycle mails and
  any cold or warm outreach.
- [references/senior-practice.md](references/senior-practice.md): load when reviewing a marketing plan, to
  check it against what experienced B2B marketers insist on and what agents get wrong.
- Depth from `coreyhaines31/marketingskills` (MIT), installed one by one, not as the whole plugin: `cro`,
  `signup`, `onboarding`, `ab-testing`, `churn-prevention`, `referrals`, `sales-enablement`, `competitors`.
  Install line in `stack-bootstrap`'s curated skills. https://github.com/coreyhaines31/marketingskills
  (verified 2026-11-03).

## Sources

- https://christophjanz.blogspot.com/2014/10/five-ways-to-build-100-million-business.html: revenue-per-account
  bands and the way to win each, 5 October 2014, verified 2026-11-04.
- https://www.forentrepreneurs.com/saas-metrics-2/: CAC payback of 5 to 7 months for the best SaaS businesses,
  anemic beyond 12, verified 2026-11-04.
- The checks G01 to G29 are reproducible with the script's self-test.
- https://www.gesetze-im-internet.de/uwg_2004/__7.html: UWG § 7, verified 2026-11-03.
- https://www.gesetze-im-internet.de/uwg_2004/__7a.html: UWG § 7a, verified 2026-11-03.
- https://www.gesetze-im-internet.de/uwg_2004/__5.html and https://www.gesetze-im-internet.de/uwg_2004/__5a.html:
  misleading claims, undisclosed commercial purpose, verified 2026-11-03.
- https://www.gesetze-im-internet.de/uwg_2004/anhang.html: Anhang Nr. 23b, 23c, verified 2026-11-03.
- https://corporate.trustpilot.com/legal/for-everyone/action-we-take, https://support.google.com/contributionpolicy/answer/7400114,
  https://legal.g2.com/community-guidelines: review platform rules, verified 2026-11-03.
