<?php

namespace App\Services;

use Illuminate\Container\Attributes\Singleton;
use Illuminate\Http\Request;

#[Singleton]
final class RequestLocale
{
    public function __construct(private readonly Request $request)
    {
    }

    public function get(): string
    {
        return $this->request->getPreferredLanguage() ?? 'en';
    }
}
