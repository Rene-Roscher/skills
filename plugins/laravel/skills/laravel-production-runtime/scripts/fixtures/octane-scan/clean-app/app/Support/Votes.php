<?php

namespace App\Support;

final class Votes
{
    private static ?\WeakMap $votes = null;

    public static function for(object $incident): array
    {
        self::$votes ??= new \WeakMap();

        return self::$votes[$incident] ??= ['opened' => 1];
    }
}
