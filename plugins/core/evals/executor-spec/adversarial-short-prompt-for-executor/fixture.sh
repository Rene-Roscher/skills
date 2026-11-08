#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
cat > src/invoice.py <<'EOF'
from decimal import Decimal


def invoice_total(lines):
    """Sum of quantity * unit price over all lines, in EUR, as Decimal."""
    return sum((Decimal(l["qty"]) * Decimal(l["unit_price"]) for l in lines), Decimal("0"))
EOF
cat > tests/test_invoice.py <<'EOF'
from decimal import Decimal

from src.invoice import invoice_total


def test_total():
    assert invoice_total([{"qty": "2", "unit_price": "9.99"}]) == Decimal("19.98")
EOF
touch src/__init__.py tests/__init__.py
git init -q
git -c user.name=t -c user.email=t@example.com add -A
git -c user.name=t -c user.email=t@example.com commit -qm init
