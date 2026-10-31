#!/bin/sh
# Laravel app on Octane with a package-registered social login driver.
# vendor/ holds short paraphrased stubs of the installed Octane listeners (fixture only).
set -eu
mkdir -p config app/Providers vendor/laravel/octane/src/Listeners
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "laravel/octane": "^2.17", "laravel/socialite": "^5.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [
  { "name": "laravel/framework", "version": "v12.53.0" },
  { "name": "laravel/octane", "version": "v2.17.5" },
  { "name": "laravel/socialite", "version": "v5.27.0" } ] }
JSON
cat > config/octane.php <<'PHP'
<?php

return [
    'server' => env('OCTANE_SERVER', 'frankenphp'),

    // Container bindings that are forgotten after every request.
    'flush' => [
        'current_workspace',
    ],
];
PHP
cat > app/Providers/AppServiceProvider.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Laravel\Socialite\Facades\Socialite;

final class AppServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        // Community driver, registered once when the worker boots.
        Socialite::extend('acme', fn ($app) => Socialite::buildProvider(\App\Auth\AcmeProvider::class, config('services.acme')));
    }
}
PHP
cat > vendor/laravel/octane/src/ApplicationGateway.php <<'PHP'
<?php
// Fixture stub, paraphrased from laravel/octane v2.17.5.
namespace Laravel\Octane;

class ApplicationGateway
{
    public function terminate($request, $response): void
    {
        $this->sandbox->make(\Illuminate\Contracts\Http\Kernel::class)->terminate($request, $response);
        $this->dispatchEvent($this->sandbox, new Events\RequestTerminated($this->app, $this->sandbox, $request, $response));

        $route = $request->route();
        if ($route instanceof \Illuminate\Routing\Route && method_exists($route, 'flushController')) {
            $route->flushController(); // the controller instance is dropped after each request
        }
    }
}
PHP
cat > vendor/laravel/octane/src/Listeners/PrepareSocialiteForNextOperation.php <<'PHP'
<?php
// Fixture stub, paraphrased from laravel/octane v2.17.5. Runs before every operation.
namespace Laravel\Octane\Listeners;

use Laravel\Socialite\Contracts\Factory;

class PrepareSocialiteForNextOperation
{
    public function handle($event): void
    {
        if (! $event->sandbox->resolved(Factory::class)) {
            return;
        }
        $factory = $event->sandbox->make(Factory::class);
        if (method_exists($factory, 'forgetDrivers')) {
            $factory->forgetDrivers();             // drops cached driver instances, keeps extensions
            $factory->setContainer($event->sandbox);
        }
    }
}
PHP
cat > vendor/laravel/octane/src/Listeners/FlushTemporaryContainerInstances.php <<'PHP'
<?php
// Fixture stub, paraphrased from laravel/octane v2.17.5.
namespace Laravel\Octane\Listeners;

class FlushTemporaryContainerInstances
{
    public function handle($event): void
    {
        $event->app->forgetScopedInstances();
        foreach ($event->sandbox->make('config')->get('octane.flush', []) as $binding) {
            $event->app->forgetInstance($binding); // a forgotten manager is rebuilt without its extensions
        }
    }
}
PHP
