<?php

namespace App\Support;

final class Catalog
{
    private static ?array $entries = null;

    public static function entries(): array
    {
        return self::$entries ??= json_decode((string) file_get_contents(__DIR__ . '/catalog.json'), true);
    }
}
