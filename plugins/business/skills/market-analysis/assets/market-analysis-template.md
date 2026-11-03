# Market analysis: [product], [segment]

prepared: [YYYY-MM-DD]
valid_until: [YYYY-MM-DD, 3 to 6 months after prepared]
Status: Current
Owner: [name]
Skills: market-analysis
Feeds: `docs/product/market.md`, `docs/business/model.md`, `docs/product/pricing.md`
Previous: [link to the previous analysis, or none]

## Scope

- Segment: [who buys, company size, region, language]. Example: venues with 5 to 50 staff that take
  bookings online, German-speaking countries.
- Decisions this analysis serves: [for example the price and limits of a new Team plan]
- Pages read: [region, currency, language, logged out, VPN or not]
- Not covered: [segments, regions or company kinds left out, and why]

## Reference workloads

Customers described by the usage that drives price in this market. Every normalized price below is the monthly
net cost of one of these.

| ID | Customer | Usage that drives price |
|---|---|---|
| W1 | [small, for example a freelancer] | [for example 1 user, 20 invoices a month, 1 bank account] |
| W2 | [typical paying customer] | [ ] |
| W3 | [large customer the product wants] | [ ] |

## Companies

| # | Company | Kind | Why included |
|---|---|---|---|
| 1 | [name] | direct | [same buyer, same job] |
| 2 | [name] | incumbent | [what most prospects use today] |
| 3 | [spreadsheet and email] | workaround | [doing nothing or a manual process] |
| 4 | [name] | top-tier | [the level the product wants to reach] |

Kinds: direct, adjacent (stretched to cover the job), incumbent (what the customer uses today), workaround
(spreadsheet, manual process, an intern, an agency), top-tier, new-entrant. Cover 10 to 30 companies.

## Facts

One fact per row. Every number in this file traces back to a row here.

| ID | Company | Field | Fact | Source | Accessed | Label |
|---|---|---|---|---|---|---|
| F001 | [name] | pricing | [Plan: amount, currency, per unit, per month or year, billed monthly or annually, net or gross] | [https://...] | [YYYY-MM-DD] | verified |
| F002 | [name] | limits | [what the plan caps: users, records, storage, API calls] | [https://...] | [YYYY-MM-DD] | verified |
| F003 | [name] | pricing | not public; [page checked, for example "pricing page asks for a demo"] | [https://...] | [YYYY-MM-DD] | verified |
| F004 | [name] | reviews | [theme, count of reviews naming it, sample size, date range] | [https://...] | [YYYY-MM-DD] | reported |
| F005 | [name] | limits | [conclusion], from F001 and F002 | [https://...] | [YYYY-MM-DD] | inferred |

Fields: positioning, target, pricing, value-metric, limits, free-tier, annual-discount, features, gaps,
channels, reviews, changelog, team, funding, other.
Labels: verified (read today on the primary source), reported (third party, user statement, review, not
confirmed by the company), inferred (reasoned from the named facts).

## Normalized prices

Monthly net cost of each reference workload on the cheapest plan that covers it, in [currency].

| Company | W1 (plan) | W2 (plan) | W3 (plan) | Basis |
|---|---|---|---|---|
| [name] | [amount (plan)] | [ ] | [ ] | F001, F002 |

## Price history

| Company | Earlier price (date, archived snapshot URL) | Current (fact ID) | Change |
|---|---|---|---|
| [name] | [amount, YYYY-MM-DD, https://web.archive.org/...] | F001 | [for example +20 %, value metric changed] |

## Synthesis

### Price corridor

[Per workload: lowest, median and highest normalized price among direct competitors, with the fact IDs. Where
the incumbent and the top tier sit relative to the corridor.]

### Table stakes

[Capabilities on the entry plan of every relevant alternative, each with the fact IDs that show it.]

### White spaces

[Jobs or segments no alternative serves well, with the facts or review themes that show it.]

### Threats

[Price moves, bundling by a larger player, new entrants, free tiers that cap the market, with fact IDs.]

### Recommendations

1. [Recommendation in one sentence, and what it would change]. Evidence: F001, F007

### Open questions

1. [What is still unknown, why it matters, and how to find out]
