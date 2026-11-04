#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/product docs/marketing
printf '# Product brief: time tracking for small agencies\n\nBuyer: agency owner, 5 to 30 people, Germany.\n' > docs/product/brief.md
printf '# Pricing model\n\nAgency plan 99 EUR per month net; typical customer pays 1188 EUR per year; gross margin 75 percent; payback target 12 months.\n' > docs/product/pricing.md
python3 - <<'PY'
import datetime as dt
t = dt.date.today()
d = lambda n: (t + dt.timedelta(days=n)).isoformat()
plan = f"""# Go-to-market plan: time tracking, small agencies

created: {d(0)}
Owner: Founder
Skills: go-to-market

## Inputs

| Input | Value | Source |
|---|---|---|
| Product brief | docs/product/brief.md | product-strategy |
| Pricing model | docs/product/pricing.md | pricing-and-unit-economics |
| Currency | EUR | pricing model |
| Contract value per year | 1188 | pricing model |
| Gross margin percent | 75 | pricing model |
| Payback target months | 12 | pricing model |

## Sales motion

| Field | Value |
|---|---|
| Motion | self-serve |
| Sales cost per won deal | 0 |
| Founder-led until | first 20 paying customers |
| Reason | 1188 per year is below the 10000 band; ceiling 891 |

## Channels

| # | Channel | Evidence buyer is there | Target cost per paying customer | Attribution field | Start date | Read date | Stop/scale rule | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | LinkedIn ads | agency owners use LinkedIn | 800 | signup_source=linkedin | {d(1)} | {d(11)} | stop above 891 after 2 cohorts | planned |
| 2 | Webinar with a design community | 3 of 8 interviewed owners read its newsletter | 400 | signup_source=webinar | {d(1)} | {d(45)} | stop below 5 paying customers | planned |
| 3 | Comparison pages | 90 searches a month for the problem | 300 | signup_source=search | {d(3)} | {d(60)} | stop above 891 after 3 months | planned |

## Outreach and mail

| # | Message | Channel | Recipients from | Country | Type | Legal basis | Proof stored where |
|---|---|---|---|---|---|---|---|
| 1 | Sign-up confirmation | email | own sign-up form | DE | transactional | n/a | n/a |
| 2 | Webinar invitation | email | own customers and trial users | DE | advertising | § 7 Abs. 3 | |

## Launch checklist

Launch date: {d(1)}

- [x] Positioning and price stored; launch message checked against the product-truth table.
- [ ] A new account reaches its first result without help; tested on a fresh account.
- [x] Attribution on every launch link; the sign-up source stored on the account.
- [ ] Directory and marketplace profiles complete and current.
- [x] Owned audience contacted only with consent or under § 7 Abs. 3 UWG.
- [ ] Support capacity and a known-issues note for launch day.
- [x] Changelog and docs updated; pages for new features live and indexed.
- [x] A read date and the metrics to report: attributed sign-ups, paying customers, cost per paying customer.

## Owners

| Area | Owner |
|---|---|
| Plan and budget | Founder |
| Outreach and mail, approves every send | Founder |
"""
open("docs/marketing/gtm-plan.md", "w", encoding="utf-8").write(plan)
PY
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add go-to-market plan'
