#!/usr/bin/env bash
set -euo pipefail
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "rates", "private": true, "scripts": { "test": "node --test" } }
JSON
cat > src/rates.js <<'JS'
'use strict';
const http = require('node:http');
// Reads the current exchange rate from the local rates service.
function fetchRate(currency) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:59999/rates/${currency}`, (res) => {
      let body = '';
      res.on('data', (c) => { body += c; });
      res.on('end', () => resolve(JSON.parse(body).rate));
    }).on('error', reject);
  });
}
module.exports = { fetchRate };
JS
cat > test/rates.test.js <<'JS'
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { fetchRate } = require('../src/rates');

test('reads the EUR rate from the rates service', async () => {
  const rate = await fetchRate('EUR');
  assert.ok(rate > 0);
});
JS
