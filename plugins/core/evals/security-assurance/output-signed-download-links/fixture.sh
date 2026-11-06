#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p invoices tests storage/invoices
printf '%%PDF-1.4 fake invoice 1001\n' > storage/invoices/1001.pdf
cat > invoices/__init__.py <<'PY'
PY
cat > invoices/app.py <<'PY'
"""Tiny invoice service. Logged-in customers download their own invoices at /invoices/[id].pdf."""
from pathlib import Path

STORAGE = Path(__file__).resolve().parent.parent / "storage" / "invoices"


def download(user, invoice_id: str):
    """Return (status, body). Only the owner may download."""
    if user is None or invoice_id not in user.get("invoices", []):
        return 404, b"not found"
    f = STORAGE / f"{invoice_id}.pdf"
    if not f.is_file():
        return 404, b"not found"
    return 200, f.read_bytes()
PY
cat > tests/__init__.py <<'PY'
PY
cat > tests/test_app.py <<'PY'
import unittest

from invoices.app import download


class DownloadTest(unittest.TestCase):
    def test_owner_downloads(self):
        status, body = download({"invoices": ["1001"]}, "1001")
        self.assertEqual(status, 200)
        self.assertIn(b"1001", body)

    def test_other_user_gets_404(self):
        self.assertEqual(download({"invoices": []}, "1001")[0], 404)


if __name__ == "__main__":
    unittest.main()
PY
cat > README.md <<'MD'
# invoices

Run the tests with `python3 -m unittest`.
MD
git add -A
git -c user.email=t@example.org -c user.name=t commit -qm "feat: add invoice downloads for owners"
