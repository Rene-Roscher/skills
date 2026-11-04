#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p dist/en
cat > dist/robots.txt <<'TXT'
User-agent: *
Allow: /

User-agent: OAI-SearchBot
User-agent: Claude-SearchBot
Disallow: /
TXT
cat > dist/index.html <<'HTML'
<!doctype html><html lang="en"><head>
<title>Project planning for agencies</title>
<link rel="canonical" href="https://www.example.com/">
</head><body><h1>Plan client projects without spreadsheets</h1><p>Timelines, budgets and approvals in one board.</p></body></html>
HTML
cat > dist/en/pricing.html <<'HTML'
<!doctype html><html lang="en"><head>
<title>Pricing - Project planning for agencies</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://www.example.com/en/pricing">
</head><body><h1>Pricing</h1><p>Starter, Team and Agency plans, billed monthly or yearly.</p></body></html>
HTML
cat > dist/en/integrations.html <<'HTML'
<!doctype html><html lang="en"><head>
<title>Integrations - Project planning for agencies</title>
<link rel="canonical" href="https://www.example.com/en/integrations">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Project planner","aggregateRating":{"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"210"}}</script>
</head><body><h1>Integrations</h1><p>Connect your calendar, chat and invoicing tools.</p></body></html>
HTML
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'build: add static output'
