#!/usr/bin/env bash
set -euo pipefail
{
  for i in $(seq 1 18); do echo "src/ui/components/Widget$i.vue"; done
  for i in $(seq 1 12); do echo "src/ui/pages/Page$i.vue"; done
  for i in $(seq 1 6); do echo "src/api/handlers/calendar$i.js"; done
  echo "src/billing/refund.js"
  echo "src/billing/invoice-total.js"
  echo "src/auth/session.js"
  echo "src/tenancy/scope.js"
} > changed-files.txt
