#!/bin/sh
# A dashboard controller that computes every widget, including a paid API call, inside one request, uncached.
set -eu
mkdir -p app/Http/Controllers docs
cat > app/Http/Controllers/DashboardController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Services\HelpdeskClient;
use App\Services\PaymentReportingClient;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;

class DashboardController extends Controller
{
    public function show(Request $request, PaymentReportingClient $payments, HelpdeskClient $helpdesk)
    {
        $workspaceId = $request->user()->workspace_id;

        return Inertia::render('Dashboard', [
            'openAmount' => DB::table('invoices')->where('workspace_id', $workspaceId)->whereNull('paid_at')->sum('total'),
            'revenueByMonth' => DB::table('payments')
                ->where('workspace_id', $workspaceId)
                ->selectRaw("date_trunc('month', paid_at) as month, sum(amount) as total")
                ->groupBy('month')->orderBy('month')->get(),
            'failedPayments' => $payments->failedPayments($workspaceId, now()->subDays(30)),
            'openTickets' => $helpdesk->openTicketsByCustomer($workspaceId),
            'topCustomers' => DB::table('invoices')->where('workspace_id', $workspaceId)
                ->selectRaw('customer_id, sum(total) as total')->groupBy('customer_id')
                ->orderByDesc('total')->limit(10)->get(),
        ]);
    }
}
PHP
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Multi-tenant: yes. Largest workspace: 1.2 million invoices, 900,000 payments over six years, 40 users.
- The dashboard is the start page after login; about 25 views per user per day.
- Payment provider reporting API: about 1.5 s per call, 0.002 EUR per call above 10,000 calls a month.
- Helpdesk API: about 0.8 s per call, rate limit 60 calls a minute per account.
- Cache: Redis with tags.
MD
