#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/specs
cat > docs/specs/payment-reminders.md <<'MD'
# Payment reminders

- A reminder email goes to the client 3 days before the due date, and a second one on the due date.
- Both are on by default for new accounts and can be switched off per client.
- The email contains a "Pay now" button that opens the hosted payment page.
- Late fees are not part of this feature.
MD
