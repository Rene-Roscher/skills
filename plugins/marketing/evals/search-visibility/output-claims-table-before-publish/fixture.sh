#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p config site docs/claims
cat > config/plans.json <<'JSON'
{
  "team": {
    "price_eur_month": 39,
    "projects": 50,
    "members": 10,
    "file_storage_gb": 100
  }
}
JSON
cat > site/features.html <<'HTML'
<!doctype html><html lang="en"><head><title>Features - Project planner</title></head><body>
<h1>Features</h1>
<p>Time tracking that syncs every 5 minutes.</p>
</body></html>
HTML
cat > site/pricing.html <<'HTML'
<!doctype html><html lang="en"><head><title>Pricing - Project planner</title></head><body>
<h1>Team plan</h1>
<p>39 € per month for 50 projects and 15 team members, 100 GB file storage.</p>
<p>Time tracking syncs every 5 minutes. Hosted in Frankfurt.</p>
</body></html>
HTML
cat > docs/claims/pricing.md <<'MD'
# Claims table: site/pricing.html

| claim | value as on page | source | checked on |
|---|---|---|---|
| Team price per month | 39 | config/plans.json:3 | 2026-11-02 |
| Projects on Team | 50 | config/plans.json:4 | 2026-11-02 |
| Team members on Team | 15 | config/plans.json:5 | 2026-11-02 |
| File storage on Team | 100 | config/plans.json:6 | 2026-11-02 |
| Time tracking sync interval | 5 minutes | site/features.html:3 | 2026-11-02 |
| Hosting location | Frankfurt |  | 2026-11-02 |
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add pricing page and claims table'
