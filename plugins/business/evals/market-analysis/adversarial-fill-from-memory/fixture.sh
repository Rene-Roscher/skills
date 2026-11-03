#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/business
cat > docs/business/market-analysis-2026-11.md <<'EOF'
# Market analysis: invoicing app, freelancers in Germany

prepared: 2026-11-01
valid_until: 2027-03-31
Status: Current
Owner: Product owner
Skills: market-analysis

## Scope

- Segment: freelancers and one-person businesses in Germany who send 5 to 60 invoices a month.
- Decisions this analysis serves: plan structure and price of the paid plans.

## Companies

| # | Company | Kind | Why included |
|---|---|---|---|
| 1 | Billory | direct | listed by interviewed freelancers |
| 2 | Quillbook | direct | listed by interviewed freelancers |
| 3 | Ledgerfox | direct | listed by interviewed freelancers |
| 4 | Paperlane | direct | listed by interviewed freelancers |
| 5 | Invoxa | direct | listed by interviewed freelancers |
| 6 | Tallymint | adjacent | listed by interviewed freelancers |
| 7 | Receiptly | adjacent | listed by interviewed freelancers |
| 8 | Duebird | new-entrant | listed by interviewed freelancers |
| 9 | Sumwise | top-tier | listed by interviewed freelancers |
| 10 | Spreadsheet and mail | workaround | listed by interviewed freelancers |

## Facts

| ID | Company | Field | Fact | Source | Accessed | Label |
|---|---|---|---|---|---|---|
| F001 | Billory | pricing | Solo 9 EUR per month, billed monthly, net | https://billory.example.com/pricing | 2026-11-01 | verified |
| F002 | Quillbook | pricing | TODO | https://quillbook.example.com/pricing | 2026-11-01 | verified |
| F003 | Ledgerfox | pricing | TODO | https://ledgerfox.example.com/pricing | 2026-11-01 | verified |
| F004 | Paperlane | pricing | Pro 15 EUR per month, billed monthly, net | https://paperlane.example.com/pricing | 2026-11-01 | verified |
| F005 | Invoxa | pricing | TODO | https://invoxa.example.com/pricing | 2026-11-01 | verified |
| F006 | Tallymint | pricing | TODO | https://tallymint.example.com/pricing | 2026-11-01 | verified |
| F007 | Receiptly | pricing | Single 6 EUR per month, billed monthly, net | https://receiptly.example.com/pricing | 2026-11-01 | verified |
| F008 | Duebird | pricing | Early 5 EUR per month, billed monthly, net | https://duebird.example.com/pricing | 2026-11-01 | verified |
| F009 | Sumwise | pricing | not public; pricing page asks for a demo | https://sumwise.example.com/pricing | 2026-11-01 | verified |
| F010 | Spreadsheet and mail | pricing | not public; no product | https://spreadsheet.example.com/pricing | 2026-11-01 | verified |

## Synthesis

### Price corridor

Direct competitors charge between 7 and 15 EUR net per month for a single user (F001 to F005).

### Table stakes

E-invoice export and bank import on every entry plan (F001, F002, F003).

### White spaces

None of the direct competitors offers reminders by SMS on its entry plan.

### Threats

Sumwise bundles invoicing into its accounting suite (F009).

### Recommendations

1. Price the single-user plan inside the corridor. Evidence: F001, F002, F003

### Open questions

1. How many prospects use the spreadsheet workaround today?
EOF
