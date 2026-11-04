<?php

namespace App\Services;

final class Money
{
    public function __construct(private readonly string $currency = 'EUR')
    {
    }

    public function format(int $cents): string
    {
        return number_format($cents / 100, 2) . ' ' . $this->currency;
    }
}
