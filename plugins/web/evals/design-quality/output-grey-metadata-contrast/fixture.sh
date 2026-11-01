#!/bin/sh
set -eu
mkdir -p public
cat > public/invoices.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Invoices</title>
  <style>
    :root { color-scheme: light dark; }
    body { margin: 0; padding: 24px; font: 16px/24px sans-serif; background: #ffffff; color: #171717; }
    .row { padding: 12px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.08); }
    .meta { font-size: 13px; color: #4b5563; }
    @media (prefers-color-scheme: dark) {
      body { background: #111827; color: #f9fafb; }
      .row { border-bottom-color: rgba(255, 255, 255, 0.12); }
      .meta { color: #9ca3af; }
    }
  </style>
</head>
<body>
  <div class="row">Invoice 1042 &middot; Northwind Studio <div class="meta">Sent 3 days ago, due 14 December</div></div>
  <div class="row">Invoice 1041 &middot; Contoso Ltd <div class="meta">Paid 28 November</div></div>
</body>
</html>
HTML
