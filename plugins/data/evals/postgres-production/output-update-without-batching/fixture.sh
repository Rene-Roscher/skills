#!/usr/bin/env bash
set -euo pipefail
mkdir -p db/migrations
cat > db/migrations/0215_add_currency.sql <<'SQL'
ALTER TABLE orders ADD COLUMN currency text;
UPDATE orders SET currency = 'EUR';
ALTER TABLE orders ALTER COLUMN currency SET NOT NULL;
SQL
