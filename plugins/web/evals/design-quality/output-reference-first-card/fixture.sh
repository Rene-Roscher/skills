#!/bin/sh
set -eu
mkdir -p public
cat > public/tokens.css <<'CSS'
:root {
  --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-6: 24px;
  --radius-control: 6px; --radius-card: 12px;
  --fg: #171717; --fg-muted: #4d4d4d; --bg: #ffffff; --border: rgba(0, 0, 0, 0.08);
  --font-sm: 14px; --font-md: 16px; --font-lg: 20px;
}
CSS
cat > public/settings.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Settings</title>
  <link rel="stylesheet" href="tokens.css">
  <style>
    body { margin: 0; font: var(--font-md)/24px sans-serif; background: var(--bg); color: var(--fg); padding: var(--space-6); }
    .card { border: 1px solid var(--border); border-radius: var(--radius-card); padding: var(--space-4); margin-bottom: var(--space-4); }
    .card h2 { font-size: var(--font-lg); margin: 0 0 var(--space-2); }
    .card p { font-size: var(--font-sm); color: var(--fg-muted); margin: 0 0 var(--space-3); }
    .field { height: 32px; border: 1px solid var(--border); border-radius: var(--radius-control); padding: 0 var(--space-3); }
  </style>
</head>
<body>
  <section class="card" data-testid="card-profile">
    <h2>Profile</h2>
    <p>Name and billing address shown on invoices.</p>
    <input class="field" aria-label="Company name" value="Northwind Studio">
  </section>
  <section class="card" data-testid="card-currency">
    <h2>Currency</h2>
    <p>Used for new invoices.</p>
    <input class="field" aria-label="Currency" value="EUR">
  </section>
</body>
</html>
HTML
