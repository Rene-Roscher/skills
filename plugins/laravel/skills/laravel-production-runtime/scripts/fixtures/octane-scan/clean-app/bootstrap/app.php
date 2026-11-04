<?php

use App\Services\Money;
use Illuminate\Foundation\Application;

return Application::configure(basePath: dirname(__DIR__))
    ->withSingletons([Money::class])
    ->create();
