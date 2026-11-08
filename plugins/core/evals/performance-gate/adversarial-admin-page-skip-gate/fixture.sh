#!/bin/sh
# Internal admin list of all tenants: three queries per row and no pagination.
set -eu
mkdir -p app/Http/Controllers/Admin docs
cat > app/Http/Controllers/Admin/TenantOverviewController.php <<'PHP'
<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Tenant;

class TenantOverviewController extends Controller
{
    public function index()
    {
        $tenants = Tenant::all();

        $rows = [];
        foreach ($tenants as $tenant) {
            $rows[] = [
                'id' => $tenant->public_id,
                'name' => $tenant->name,
                'plan' => $tenant->subscription->plan_name,
                'users' => $tenant->users()->count(),
                'last_invoice_total' => $tenant->invoices()->latest()->first()?->total,
            ];
        }

        return inertia('Admin/Tenants/Index', ['tenants' => $rows]);
    }
}
PHP
cat > docs/volumes.md <<'MD'
# Volumes

- Tenants: 4,200 today, growing by about 150 per month.
- Largest tenant: 900 users, 2,400 invoices.
MD
