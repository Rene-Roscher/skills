<?php

declare(strict_types=1);

namespace App\Providers;

use App\Services\{Clock, CurrentAccount, Money};
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    /** Bindings Laravel registers as singletons: stateless only. */
    public array $singletons = [
        Money::class => Money::class,
    ];

    private static bool $booted = false;

    public function register(): void
    {
        // Per request and per job: scoped, never singleton.
        $this->app->scoped(CurrentAccount::class);

        // A resolver closure reads the current request on every call.
        $this->app->singleton(Clock::class, fn (Application $app) => new Clock(fn () => $app['request']));
    }

    public function boot(): void
    {
        JsonResource::withoutWrapping();
        static::$booted = true;
        $this->app->instance('money.default', new Money('EUR'));
    }
}
