#!/bin/sh
# Laravel app on Octane: a singleton reads the authenticated user in its constructor.
set -eu
mkdir -p config app/Reports app/Providers app/Http/Controllers
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
    'flush' => [],
];
PHP
cat > app/Reports/ReportScope.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Reports;

final class ReportScope
{
    private readonly int $userId;

    public function __construct()
    {
        $this->userId = (int) auth()->id();
    }

    /** @return array{owner_id: int} */
    public function filters(): array
    {
        return ['owner_id' => $this->userId];
    }
}
PHP
cat > app/Providers/AppServiceProvider.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Providers;

use App\Reports\ReportScope;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton(ReportScope::class);
    }
}
PHP
cat > app/Http/Controllers/ReportController.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Reports\ReportScope;

final class ReportController
{
    public function index(ReportScope $scope): array
    {
        return $scope->filters();
    }
}
PHP
