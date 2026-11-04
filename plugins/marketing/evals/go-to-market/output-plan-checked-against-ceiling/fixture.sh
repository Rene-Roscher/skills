#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/product
cat > docs/product/brief.md <<'MD'
# Product brief: booking system for driving schools

Buyer: owner of a driving school with 2 to 15 instructors in Germany.
Alternative today: paper calendar plus phone and messenger.
Positioning: lessons, instructors and payments in one booking calendar.
MD
cat > docs/product/pricing.md <<'MD'
# Pricing model

- School plan: 49 EUR per month, net, billed monthly. A typical paying school pays 588 EUR per year.
- Gross margin at typical use: 80 percent (hosting, SMS, payment fee, support time).
- Payback target for acquisition cost: 12 months (owner decision).
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add brief and pricing model'
