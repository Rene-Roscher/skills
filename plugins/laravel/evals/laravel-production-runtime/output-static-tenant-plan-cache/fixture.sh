#!/bin/sh
# Multi-tenant Laravel app on Octane: the tenant is bound per request, PlanResolver queries on every call.
set -eu
mkdir -p config app/Billing app/Models app/Http/Middleware app/Http/Controllers app/Providers
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "laravel/octane": "^2.17" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [
  { "name": "laravel/framework", "version": "v12.53.0" },
  { "name": "laravel/octane", "version": "v2.17.5" } ] }
JSON
cat > config/octane.php <<'PHP'
<?php

return [
    'server' => env('OCTANE_SERVER', 'frankenphp'),

    'flush' => [
        'current_tenant',
    ],
];
PHP
cat > app/Http/Middleware/IdentifyTenant.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Models\Tenant;
use Closure;
use Illuminate\Http\Request;

final class IdentifyTenant
{
    public function handle(Request $request, Closure $next): mixed
    {
        app()->forgetInstance('current_tenant');

        $tenant = Tenant::query()->where('domain', $request->getHost())->first();
        if ($tenant === null) {
            return $next($request);
        }

        app()->instance('current_tenant', $tenant);

        return $next($request);
    }
}
PHP
cat > app/Models/Tenant.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

final class Tenant extends Model
{
}
PHP
cat > app/Models/Plan.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

final class Plan extends Model
{
}
PHP
cat > app/Billing/PlanResolver.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Billing;

use App\Models\Plan;

final class PlanResolver
{
    public function current(): Plan
    {
        $tenant = app('current_tenant');

        return Plan::query()->whereKey($tenant->plan_id)->firstOrFail();
    }
}
PHP
cat > app/Http/Controllers/BookingController.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Billing\PlanResolver;

final class BookingController
{
    public function index(PlanResolver $plans): array
    {
        return ['limit' => $plans->current()->booking_limit, 'name' => $plans->current()->name];
    }
}
PHP
cat > app/Providers/AppServiceProvider.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
    }
}
PHP
