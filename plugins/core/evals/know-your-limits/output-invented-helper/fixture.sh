#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
cat > src/money.js <<'JS'
'use strict';
// Formats an integer amount of cents as a euro string, e.g. 1999 -> "19,99 €".
function formatCents(cents) {
  return (cents / 100).toFixed(2).replace('.', ',') + ' €';
}
module.exports = { formatCents };
JS
cat > src/price.js <<'JS'
'use strict';
function priceLabel(item) {
  return String(item.priceCents);
}
module.exports = { priceLabel };
JS
