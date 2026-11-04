<?php

namespace App\Services;

final class QuotaService
{
    private array $byTenant = [];
    private array $labels = [];

    public function forTenant(object $tenant, string $key): int
    {
        $memo = $tenant->id . ':' . $key;

        return $this->byTenant[$memo] ??= 10;
    }

    public function label(object $org): string
    {
        return $this->labels["{$org->id}:label"] ??= 'quota';
    }
}
