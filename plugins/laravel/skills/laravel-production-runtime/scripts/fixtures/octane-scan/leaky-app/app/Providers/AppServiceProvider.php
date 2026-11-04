<?php

declare(strict_types=1);

namespace App\Providers;

use App\Services\CurrentAccount;
use App\Services\ExportSigner;
use App\Services\Pricing;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton(CurrentAccount::class);

        $this->app->singleton(Pricing::class, fn (Application $app) => new Pricing($app['request']->header('X-Currency', 'EUR')));

        $this->app->singleton(ExportSigner::class);

        $this->app->singleton('report.clock', fn (Application $app) => new \App\Services\Clock(fn () => $app['request']));
        $this->app->singleton(\App\Services\AuditTrail::class);
    }
}
