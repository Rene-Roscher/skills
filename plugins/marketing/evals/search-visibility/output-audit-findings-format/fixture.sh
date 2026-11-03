#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p dist/en dist/de
cat > dist/en/features.html <<'HTML'
<!doctype html><html lang="en"><head>
<title>Features - Invoicing app</title>
<link rel="canonical" href="https://www.example.com/">
<link rel="alternate" hreflang="en" href="https://www.example.com/en/features">
<link rel="alternate" hreflang="de" href="https://www.example.com/de/funktionen">
</head><body><h1>Send invoices that get paid</h1><p>Payment links, reminders and e-invoice export.</p></body></html>
HTML
cat > dist/de/funktionen.html <<'HTML'
<!doctype html><html lang="de"><head>
<title>Funktionen - Rechnungs-App</title>
<link rel="canonical" href="https://www.example.com/de/funktionen">
</head><body><h1>Rechnungen, die bezahlt werden</h1><p>Zahlungslinks, Erinnerungen und E-Rechnung.</p></body></html>
HTML
cat > dist/en/pricing.html <<'HTML'
<!doctype html><html lang="en"><head>
<title>Pricing - Invoicing app</title>
<link rel="canonical" href="https://www.example.com/en/pricing">
</head><body><div id="app"></div><script src="/assets/pricing.js"></script></body></html>
HTML
cat > dist/en/old-pricing.html <<'HTML'
<!doctype html><html><head><meta http-equiv="refresh" content="0; url=/en/pricing"></head><body></body></html>
HTML
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'build: add static output'
