#!/usr/bin/env bash
set -euo pipefail
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "invoicing", "private": true, "scripts": { "test": "node --test" } }
JSON
cat > src/invoice.js <<'JS'
'use strict';
// Sums line totals in cents. Each line: { unitCents, qty, discountPct }.
function invoiceTotalCents(lines) {
  return lines.reduce((sum, l) => sum + l.unitCents * l.qty * (1 - l.discountPct / 100), 0);
}
module.exports = { invoiceTotalCents };
JS
cat > src/customer.js <<'JS'
'use strict';
// Retruns the display name for a customer record.
function displayName(customer) {
  return customer.company.name + ' (' + customer.contact + ')';
}
module.exports = { displayName };
JS
cat > test/invoice.test.js <<'JS'
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { invoiceTotalCents } = require('../src/invoice');

test('sums undiscounted lines', () => {
  assert.strictEqual(invoiceTotalCents([{ unitCents: 1000, qty: 2, discountPct: 0 }]), 2000);
});
JS
