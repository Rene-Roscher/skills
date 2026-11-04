<?php

namespace App\Services;

use Closure;

final class Clock
{
    public function __construct(private readonly Closure $request)
    {
    }

    public function zone(): string
    {
        return ($this->request)()->header('X-Zone', 'UTC');
    }
}
