#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/shared src/invoices
touch src/__init__.py src/shared/__init__.py src/invoices/__init__.py
cat > src/shared/money.py <<'PY'
def format_money(cents, currency="EUR"):
    # Format an integer cent amount, for example 1234567 -> 12,345.67 EUR
    whole, frac = divmod(abs(cents), 100)
    sign = "-" if cents < 0 else ""
    return f"{sign}{whole:,}.{frac:02d} {currency}"
PY
cat > src/invoices/summary.py <<'PY'
def summary_lines(invoice):
    lines = [f"Invoice {invoice['id']}"]
    for item in invoice["items"]:
        lines.append(f"{item['name']} x{item['qty']}")
    return lines
PY
