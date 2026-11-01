#!/usr/bin/env bash
set -euo pipefail
mkdir -p db/migrations
cat > db/migrations/0107_invoice_constraints.sql <<'SQL'
ALTER TABLE invoices
  ADD CONSTRAINT invoices_customer_fk FOREIGN KEY (customer_id) REFERENCES customers (id);
ALTER TABLE invoices ADD CONSTRAINT invoices_total_positive CHECK (total_cents >= 0);
ALTER TABLE invoices ALTER COLUMN issued_at SET NOT NULL;
SQL
