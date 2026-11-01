#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
touch src/__init__.py tests/__init__.py
cat > src/refunds.py <<'PY'
class RefundError(Exception):
    pass


def refund(invoice, amount_cents, requester_tenant, store):
    if invoice["tenant"] != requester_tenant:
        raise RefundError("forbidden")
    if amount_cents <= 0:
        raise RefundError("amount must be positive")
    already = sum(r["amount"] for r in store if r["invoice"] == invoice["id"])
    if already + amount_cents > invoice["paid_cents"]:
        raise RefundError("exceeds paid amount")
    store.append({"invoice": invoice["id"], "amount": amount_cents})
    return amount_cents
PY
