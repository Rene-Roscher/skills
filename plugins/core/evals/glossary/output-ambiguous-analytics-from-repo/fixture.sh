#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p src docs
cat > package.json <<'JSON'
{
  "name": "booking-site",
  "private": true,
  "dependencies": {
    "plausible-tracker": "^0.3.9",
    "vue": "^3.4.0"
  }
}
JSON
cat > src/analytics.ts <<'TS'
import Plausible from 'plausible-tracker'

export const plausible = Plausible({ domain: 'booking.example.com' })

export function trackPricingView(): void {
  plausible.trackEvent('pricing-view')
}
TS
printf '# Booking site\n\nA small booking site. Deployment notes are in docs/deploy.md.\n' > README.md
printf '# Deploy\n\nStatic build, served by a reverse proxy.\n' > docs/deploy.md
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
