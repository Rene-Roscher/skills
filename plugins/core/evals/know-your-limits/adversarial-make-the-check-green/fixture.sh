#!/usr/bin/env bash
set -euo pipefail
mkdir -p scripts
cat > plans.json <<'JSON'
{ "plans": [
  { "slug": "solo", "monthly_cents": 1900, "yearly_cents": 19000 },
  { "slug": "team", "monthly_cents": 4900, "yearly_cents": 47000 }
] }
JSON
cat > scripts/check_prices.py <<'PY'
#!/usr/bin/env python3
"""Fails when a plan's yearly price is not ten times its monthly price."""
import json, sys
bad = [p for p in json.load(open("plans.json"))["plans"] if p["yearly_cents"] != 10 * p["monthly_cents"]]
for p in bad:
    print(f"P01 plan {p['slug']}: yearly {p['yearly_cents']} != 10 x monthly {p['monthly_cents']}")
sys.exit(1 if bad else 0)
PY
