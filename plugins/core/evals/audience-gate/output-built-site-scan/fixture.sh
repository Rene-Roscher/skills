#!/usr/bin/env bash
set -euo pipefail
mkdir -p dist/en/pricing
cat > dist/index.html <<'HTML'
<!doctype html><html lang="en"><head><title>Bookings for salons</title></head><body><main><h1>Bookings for salons</h1><p>Your clients book online, you get every booking at once.</p></main></body></html>
2026]</script></body></html>
HTML
cat > dist/en/pricing/index.html <<'HTML'
<!doctype html><html lang="en"><head><title>Pricing</title>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"Salonbook","description":"Salonbook ist die Buchungssoftware für Salons aus Deutschland, gehostet in der EU."},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"nav.pricing","item":"https://example.com/en/pricing"}]}]}</script>
</head><body><main><h1>Pricing</h1><p>Free for one chair, 19 euros a month for up to five.</p></main></body></html>
HTML
