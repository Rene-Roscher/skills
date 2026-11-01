# Model structure

Load when you create or edit the model file, or when a script finding needs interpreting. All amounts are net,
in one currency, per month.

## Input object

Every number is an object:

```json
{ "value": 0.10, "source": "SMS provider invoice 2026-09, segment price", "assumption": false }
```

- `source` names the measurement query, the invoice or the vendor page, with its date.
- `assumption: true` marks a number that is not measured yet. Results that use it print a star.
- `value: null` is allowed only for an unknown ceiling, and then the script reports `E02`.

## File layout

```json
{
  "target_gross_margin": { "value": 0.75, "source": "owner decision 2026-10", "assumption": false },
  "unit_costs": {
    "sms_segment": { "value": 0.10, "source": "provider invoice 2026-09", "assumption": false },
    "storage_gb":  { "value": 0.02, "source": "cloud invoice 2026-09", "assumption": false },
    "support_hour": { "value": 40, "source": "loaded hourly cost, finance 2026-09", "assumption": true }
  },
  "payment_fee": {
    "percent": { "value": 0.02, "source": "payment provider price list, checked 2026-10", "assumption": false },
    "fixed":   { "value": 0.25, "source": "payment provider price list, checked 2026-10", "assumption": false },
    "vat_rate_on_charge": { "value": 0.0, "source": "fee basis of the provider", "assumption": false }
  },
  "fixed_costs": [
    { "name": "base infrastructure", "value": 500, "source": "cloud invoice 2026-09", "assumption": false }
  ],
  "plans": [
    {
      "name": "free",
      "price_monthly_net": { "value": 0, "source": "plan definition", "assumption": false },
      "base_cost": { "value": 0.5, "source": "measured per-tenant overhead", "assumption": true },
      "customers": { "value": 200, "source": "tenant count query 2026-10", "assumption": false },
      "usage": { "storage_gb": { "typical": { "value": 1, "source": "p50 query", "assumption": false },
                                  "ceiling": { "value": 5, "source": "plan limit", "assumption": false } } }
    }
  ],
  "free": { "conversions_per_month": { "value": 2, "source": "billing events 2026-09", "assumption": false } },
  "churn": { "churned_customers": { "value": 1, "source": "billing events", "assumption": false },
             "customers_at_start": { "value": 20, "source": "billing events", "assumption": false } }
}
```

A plan with price `0` is treated as the free tier. `price_annual_net` is optional and adds the annual fee per
month to the output. Every `usage` key must exist in `unit_costs`.

## Findings

| Code | Meaning | Fix |
|---|---|---|
| E01 | An input has no source | Name the source or mark the input as an assumption |
| E02 | A cost driver has no ceiling | Set a plan limit or a measured high percentile |
| E03 | A plan loses money at every ceiling | Lower the limit, raise the price or meter the driver |
| E04 | A required field is missing or not a number | Complete the field |
| W01 | Typical margin below the target | Decide: price, cost or target |
| W02 | Lifetime not measurable, no churned customers | Report contribution per month instead |

Exit code 0 means no finding, 1 means at least one finding, 2 means a usage error.
