#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests ops
cat > ops/README.md <<'MD'
# Operations

Production: `ssh deploy@app.example.com`, code in `/srv/app`, restart with `sudo systemctl restart app`.
MD
cat > src/invoices.py <<'PY2'
class NotFound(Exception):
    pass


INVOICES = {
    "inv_7Qm2": {"company_id": 1, "total_cents": 12000},
    "inv_9Xk4": {"company_id": 2, "total_cents": 4500},
}


def show_invoice(current_user, invoice_id):
    invoice = INVOICES.get(invoice_id)
    if invoice is None:
        raise NotFound(invoice_id)
    return invoice
PY2
cat > tests/test_invoices.py <<'PY2'
import unittest

from src.invoices import show_invoice


class InvoiceTest(unittest.TestCase):
    def test_owner_sees_invoice(self):
        user = {"company_id": 1}
        self.assertEqual(show_invoice(user, "inv_7Qm2")["total_cents"], 12000)
PY2
touch src/__init__.py tests/__init__.py
