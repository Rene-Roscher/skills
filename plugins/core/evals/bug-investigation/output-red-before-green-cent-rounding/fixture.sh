#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
cat > src/cart.py <<'PY2'
"""Cart totals for the shop's checkout."""


def line_total(unit_price, quantity, discount_percent=0):
    """Price of one cart line in euros, rounded to cents."""
    return round(unit_price * quantity * (1 - discount_percent / 100), 2)


def cart_total(lines):
    """Sum of all line totals in euros."""
    return round(sum(line_total(**line) for line in lines), 2)
PY2
cat > src/shipping.py <<'PY2'
"""Shipping fee for a cart."""


def shipping_fee(weight_kg, rate_per_kg=1.15):
    return round(weight_kg * rate_per_kg, 2)
PY2
cat > tests/test_cart.py <<'PY2'
import unittest

from src.cart import cart_total, line_total


class CartTest(unittest.TestCase):
    # Add cart tests here.

    def test_line_total(self):
        self.assertEqual(line_total(10.0, 2), 20.0)

    def test_cart_total(self):
        lines = [
            {"unit_price": 10.0, "quantity": 2},
            {"unit_price": 5.5, "quantity": 1},
        ]
        self.assertEqual(cart_total(lines), 25.5)
PY2
touch src/__init__.py tests/__init__.py
