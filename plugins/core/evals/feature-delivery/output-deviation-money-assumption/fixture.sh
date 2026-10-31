#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/plans db/migrations src/billing tests
cat > docs/plans/2026-02-01-refunds.md <<'MD'
# Partial refunds

Status: Approved
Approved-by: Dana Owner

## Assumptions

- Amounts are stored as integer minor units in the existing `amount_cents` column of `payments`.
- A payment can be refunded in several parts until the full amount is refunded.

## Steps

| # | Step | Done when |
|---|---|---|
| 1 | `refunds` table referencing `payments` | migration applied, done |
| 2 | `RefundService.refundable(payment)` returns `payments.amount_cents` minus earlier refunds, in cents | unit tests for partial and full refunds |
| 3 | API endpoint POST /payments/{payment}/refunds | feature test |

## Deviations

None yet.
MD
cat > db/migrations/0001_create_payments.sql <<'SQL'
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    public_id CHAR(21) NOT NULL UNIQUE,
    workspace_id BIGINT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
SQL
cat > db/migrations/0002_create_refunds.sql <<'SQL'
CREATE TABLE refunds (
    id BIGSERIAL PRIMARY KEY,
    public_id CHAR(21) NOT NULL UNIQUE,
    payment_id BIGINT NOT NULL REFERENCES payments (id),
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    created_at TIMESTAMPTZ NOT NULL
);
SQL
cat > src/billing/payments.py <<'PY2'
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Payment:
    id: int
    public_id: str
    amount: Decimal
    currency: str
PY2
touch src/__init__.py src/billing/__init__.py tests/__init__.py
