#!/usr/bin/env bash
# A multi-tenant invoicing product with a brief, a business model and project facts; no dashboard yet.
set -euo pipefail
mkdir -p docs/product docs/business docs/plans app/Services
cat > docs/product/brief.md <<'MD'
# Product brief

- Buyer: finance leads at agencies with 5 to 200 staff.
- Problem: month-end close takes two days because numbers sit in three tools.
- Success metric: share of workspaces that close the month inside the product, today 18 %.
- Retention: the top reason in cancellation surveys is "we still need spreadsheets for reporting".
MD
cat > docs/business/model.md <<'MD'
# Business model

- Plans: Starter 29 EUR, Team 79 EUR, Business 199 EUR per workspace and month.
- Margin floor: infrastructure and third-party cost stay below 15 % of the plan price.
- Paid third-party calls: the payment provider's reporting API costs 0.002 EUR per call above 10,000 calls a month.
MD
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Multi-tenant: yes, every table carries workspace_id. Largest workspace: 1.2 million invoices, 40 users.
- Workspaces: 3,100 active. Plans: docs/plans/YYYY-MM-DD-slug.md.
- Cache: Redis with tags. Queue: Redis.
- Sources the product can read: invoices and payments tables (PostgreSQL), the payment provider's reporting API,
  the helpdesk API (tickets per customer).
MD
cat > app/Services/InvoiceTotals.php <<'PHP'
<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;

class InvoiceTotals
{
    public function openAmount(int $workspaceId): int
    {
        return (int) DB::table('invoices')->where('workspace_id', $workspaceId)->whereNull('paid_at')->sum('total');
    }
}
PHP
