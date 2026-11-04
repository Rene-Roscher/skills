#!/bin/sh
set -eu
mkdir -p src
cat > package.json <<'JSON'
{
  "name": "example-booking-ui",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22" },
  "dependencies": { "express": "^5.1.0" }
}
JSON
cat > src/receipt.js <<'JS'
export function receiptLine(label, amount) {
  return label + " " + amount.toFixed(2);
}
JS
