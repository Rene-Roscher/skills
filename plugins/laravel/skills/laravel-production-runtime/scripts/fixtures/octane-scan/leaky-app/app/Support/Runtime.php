<?php

namespace App\Support;

final class Runtime
{
    public function prepare(object $user): void
    {
        ini_set('memory_limit', '512M');
        date_default_timezone_set($user->timezone ?? auth()->user()->timezone);
        $GLOBALS['export_started'] = microtime(true);
        define('EXPORT_MODE', 'full');
        putenv('LC_ALL=C');
    }
}
