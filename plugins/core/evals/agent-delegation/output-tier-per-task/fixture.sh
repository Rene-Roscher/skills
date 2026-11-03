#!/usr/bin/env bash
set -euo pipefail
cat > tonight.md <<'MD'
# Work for tonight (invoicing app)

1. Find every call site of formatMoney() across the repository.
2. Change the VAT calculation so reverse-charge invoices for EU business customers carry 0 % and the legal note.
3. Update the copyright year in the footer template.
4. Design how the single-tenant database becomes multi-tenant without downtime. Two attempts with the strong
   model produced plans that lose writes during the cut-over.
MD
