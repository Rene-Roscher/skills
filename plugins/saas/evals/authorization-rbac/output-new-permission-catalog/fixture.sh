#!/bin/sh
set -eu
mkdir -p app/Enums routes tests/Feature
cat > app/Enums/Permission.php <<'EOF'
<?php

namespace App\Enums;

enum Permission: string
{
    case BookingsView = 'bookings.view';
    case BookingsCancel = 'bookings.cancel';
    case RoomsManage = 'rooms.manage';
    case ReportsView = 'reports.view';
    case TokensManage = 'tokens.manage';
    case BillingManage = 'billing.manage';
}
EOF
cat > routes/web.php <<'EOF'
<?php

use App\Enums\Permission;
use App\Http\Controllers\ReportController;
use Illuminate\Support\Facades\Route;

Route::middleware(['auth', 'tenant'])->prefix('orgs/{organization}')->group(function () {
    Route::get('/reports', [ReportController::class, 'index'])
        ->can(Permission::ReportsView->value);
});
EOF
