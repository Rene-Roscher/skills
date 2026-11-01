#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
touch src/__init__.py tests/__init__.py
cat > src/flags.py <<'PY'
# Rollout finished for everyone.
NEW_CHECKOUT = True
PY
cat > src/checkout.py <<'PY'
from src.flags import NEW_CHECKOUT


def legacy_total(items):
    total = 0
    for i in items:
        total += i["price"] * i["qty"]
    return total


def new_total(items):
    return sum(i["price"] * i["qty"] for i in items)


def checkout_total(items):
    if NEW_CHECKOUT:
        return new_total(items)
    return legacy_total(items)


def format_label(name):
    return name.strip().title()
PY
cat > tests/test_checkout.py <<'PY'
import unittest

from src.checkout import checkout_total


class CheckoutTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(checkout_total([{"price": 250, "qty": 2}, {"price": 100, "qty": 1}]), 600)


if __name__ == "__main__":
    unittest.main()
PY
