#!/usr/bin/env bash
set -euo pipefail
git init -q
mkdir -p src
cat > package.json <<'JSON'
{ "name": "shop-cart", "private": true, "scripts": { "test": "node --test" } }
JSON
cat > src/cart.js <<'JS'
'use strict';
// Discount in cents for one cart line. percent is 0 to 100.
function discountCents(priceCents, percent) {
  return Math.floor((priceCents * percent) / 100);
}
module.exports = { discountCents };
JS
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m "feat: add line discounts"
cat > src/cart.js <<'JS'
'use strict';
// Discount in cents for one cart line. percent is 0 to 100.
function discountCents(priceCents, percent) {
  return Math.round((priceCents * percent) / 100);
}
module.exports = { discountCents };
JS
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m "fix: round line discounts to the nearest cent"
