#!/usr/bin/env bash
set -euo pipefail
mkdir -p db/migrations
cat > db/migrations/0042_index_bookings.sql <<'SQL'
-- Speed up the customer booking list
BEGIN;
CREATE INDEX bookings_customer_id_idx ON bookings (customer_id);
CREATE INDEX bookings_starts_at_idx ON bookings (starts_at);
COMMIT;
SQL
printf '# Booking tool\nbookings has about 80 million rows and takes writes all day.\n' > README.md
