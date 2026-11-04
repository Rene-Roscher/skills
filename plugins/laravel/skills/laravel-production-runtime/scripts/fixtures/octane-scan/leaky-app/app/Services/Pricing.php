<?php

namespace App\Services;

final class Pricing
{
    public function __construct(public readonly string $currency)
    {
    }
}
