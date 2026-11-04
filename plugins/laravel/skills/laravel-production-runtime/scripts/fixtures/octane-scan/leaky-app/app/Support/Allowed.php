<?php

namespace App\Support;

final class Allowed
{
    public function warm(string $key, string $value): void
    {
        // octane-scan: allow OS01 keyed by a compile-time pattern, identical for every tenant
        static::$patterns[$key] = $value;

        // octane-scan: allow OS01
        static::$other[$key] = $value;
    }

    private static array $patterns = [];
    private static array $other = [];
}
