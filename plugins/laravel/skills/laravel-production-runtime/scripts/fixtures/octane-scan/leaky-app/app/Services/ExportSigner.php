<?php

namespace App\Services;

use Illuminate\Contracts\Foundation\Application;

final class ExportSigner
{
    public function __construct(private readonly Application $app)
    {
    }

    public function sign(string $payload): string
    {
        return hash_hmac('sha256', $payload, (string) $this->app['config']->get('app.key'));
    }
}
