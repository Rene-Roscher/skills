#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/product
cat > docs/product/model.json <<'JSON'
{
  "target_gross_margin": {
    "value": 0.7,
    "source": "fixture invoice 2026-09",
    "assumption": false
  },
  "unit_costs": {
    "sms_segment": {
      "value": 0.09,
      "source": "fixture invoice 2026-09",
      "assumption": false
    }
  },
  "payment_fee": {
    "percent": {
      "value": 0.015,
      "source": "fixture invoice 2026-09",
      "assumption": false
    },
    "fixed": {
      "value": 0.25,
      "source": "fixture invoice 2026-09",
      "assumption": false
    },
    "vat_rate_on_charge": {
      "value": 0.0,
      "source": "fixture invoice 2026-09",
      "assumption": false
    }
  },
  "fixed_costs": [
    {
      "name": "base infrastructure",
      "value": 400,
      "source": "fixture invoice 2026-09",
      "assumption": false
    }
  ],
  "plans": [
    {
      "name": "team",
      "price_monthly_net": {
        "value": 41,
        "source": "fixture invoice 2026-09",
        "assumption": false
      },
      "base_cost": {
        "value": 1.5,
        "source": "fixture invoice 2026-09",
        "assumption": false
      },
      "customers": {
        "value": 30,
        "source": "fixture invoice 2026-09",
        "assumption": false
      },
      "usage": {
        "sms_segment": {
          "typical": {
            "value": 60,
            "source": "fixture invoice 2026-09",
            "assumption": false
          },
          "ceiling": {
            "value": null,
            "source": "fixture invoice 2026-09",
            "assumption": false
          }
        }
      }
    }
  ]
}
JSON
printf '# Booking tool\n' > README.md
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add pricing model draft'
