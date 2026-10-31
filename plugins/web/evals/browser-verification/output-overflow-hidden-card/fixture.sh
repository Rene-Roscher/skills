#!/bin/sh
# The table is wider than its card, and the card clips it, so the document itself never scrolls sideways.
set -eu
mkdir -p public
cat > public/invoices.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Invoices</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font: 14px/1.4 sans-serif; }
    .card { margin: 16px; padding: 16px; border: 1px solid #d1d5db; overflow: hidden; }
    table { min-width: 520px; border-collapse: collapse; }
    td, th { padding: 4px 8px; text-align: left; white-space: nowrap; }
  </style>
</head>
<body>
  <div class="card" data-testid="invoice-card">
    <table data-testid="invoice-table">
      <tr><th>Number</th><th>Customer</th><th>Issued</th><th>Due</th><th>Amount</th></tr>
      <tr><td>2026-0042</td><td>Northwind Rooms</td><td>2026-10-01</td><td>2026-10-15</td><td>1,240.00 EUR</td></tr>
    </table>
  </div>
</body>
</html>
HTML
