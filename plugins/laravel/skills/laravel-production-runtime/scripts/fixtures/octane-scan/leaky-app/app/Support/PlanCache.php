<?php

declare(strict_types=1);

namespace App\Support;

use App\Models\Plan;

final class PlanCache
{
    private static array $plans = [];

    public function forCurrentTenant(): Plan
    {
        return static::$plans[auth()->user()->tenant_id] ??= Plan::query()->whereKey(1)->firstOrFail();
    }

    private static array $rows = [];

    public function row(int $id): ?array
    {
        self::$rows[$id] = Plan::query()->find($id)?->toArray();

        return self::$rows[$id];
    }

    public function label(string $code): string
    {
        static $seen = [];

        return $seen[$code] ??= $code . ':' . request()->getHost();
    }

    public function remember(string $key, string $value): void
    {
        $value = trim($value);
        static::$labels[$key] = $value;
    }

    private static array $labels = [];
}
