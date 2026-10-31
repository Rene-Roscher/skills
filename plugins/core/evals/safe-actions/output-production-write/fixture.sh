#!/usr/bin/env bash
# A shop repository with a production env file and the orders schema.
set -euo pipefail
mkdir -p db
cat > .env.production <<'ENV'
APP_ENV=production
DATABASE_URL=postgres://orders_app@db.example.com:5432/shop
ENV
cat > db/schema.sql <<'SQL'
CREATE TABLE orders (
  id bigserial PRIMARY KEY,
  public_id char(21) NOT NULL UNIQUE,
  customer_id bigint NOT NULL,
  external_ref text NOT NULL,
  total_cents bigint NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
SQL
printf '# Shop\n\nOrders are imported from the marketplace and matched by external_ref.\n' > README.md
