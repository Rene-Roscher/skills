<?php

namespace App\Services;

final class InvoiceTotals
{
    public function forUser(?int $userId): array
    {
        return ['user' => $userId, 'total' => 0];
    }
}
