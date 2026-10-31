#!/usr/bin/env bash
set -euo pipefail
mkdir -p src test
cat > package.json <<'JSON'
{
  "name": "booking-confirmations",
  "private": true,
  "scripts": { "test": "node --test", "start": "node src/server.js" }
}
JSON
cat > src/format.js <<'JS'
'use strict';
// Formats a booking date for confirmation mails as DD.MM.YYYY in UTC.
function formatBookingDate(date) {
  const d = String(date.getUTCDate()).padStart(2, '0');
  const m = String(date.getUTCMonth() + 1).padStart(2, '0');
  return `${d}.${m}.${date.getUTCFullYear()}`;
}
module.exports = { formatBookingDate };
JS
cat > src/server.js <<'JS'
'use strict';
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL is not set; the confirmation service cannot start.');
  process.exit(1);
}
require('node:http')
  .createServer((req, res) => res.end('ok'))
  .listen(3000);
JS
cat > test/format.test.js <<'JS'
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { formatBookingDate } = require('../src/format');

test('formats the month with a leading zero', () => {
  assert.strictEqual(formatBookingDate(new Date(Date.UTC(2026, 2, 5))), '05.03.2026');
});
JS
