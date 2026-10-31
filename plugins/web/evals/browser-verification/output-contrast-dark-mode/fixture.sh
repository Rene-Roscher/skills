#!/bin/sh
set -eu
mkdir -p public
cat > public/billing.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Billing</title>
  <script>
    document.documentElement.dataset.theme = localStorage.getItem('theme') || 'light'
  </script>
  <style>
    body { margin: 0; font: 16px/1.4 sans-serif; background: #ffffff; color: #111827; }
    [data-theme="dark"] body { background: #111827; color: #f9fafb; }
    .card { padding: 16px; margin: 16px; border-radius: 8px; background: #f3f4f6; }
    [data-theme="dark"] .card { background: #1f2937; }
    .muted { color: #4b5563; }
    [data-theme="dark"] .muted { color: #6b7280; }
  </style>
</head>
<body>
  <section class="card" data-testid="billing-card">
    <h2>Team plan</h2>
    <p class="muted" data-testid="billing-card-muted">Renews on 1 December. Taxes are added at checkout.</p>
  </section>
</body>
</html>
HTML
