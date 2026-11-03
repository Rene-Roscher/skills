#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy
cat > copy/payments.md <<'MD'
# Payment links on every invoice

Every invoice you send has a payment link. Your customer pays by card or bank transfer from the email, without an account.

If an invoice is still open after 14 days, we send the customer a reminder. You see who has paid on the Invoices page.

From €9 a month. No setup fee.
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add payments section'
