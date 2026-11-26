#!/usr/bin/env bash
set -euo pipefail
mkdir -p locales
cat > locales/en.json <<'JSON'
{
  "pricing": {
    "intro": "This page lists the plan as it is configured in the code. The values below are the limits we enforce.",
    "sso": "Single sign-on is coming in phase 3.",
    "calendar": "Calendar export follows in a later release.",
    "agent": "Replace <Version> with the number in your logs.",
    "annual": "TODO check wording: Pay yearly and get two months free.",
    "terraform": "The provider needs Terraform 1.5 or newer.",
    "api": "Fetch the history of an invoice with GET /v2/invoices/{id}/timeline.",
    "invoices": "Send up to 50 invoices a month on the free plan."
  }
}
JSON
