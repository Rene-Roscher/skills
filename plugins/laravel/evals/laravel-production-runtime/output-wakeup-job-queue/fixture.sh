#!/bin/sh
# Payments app with one bulk job on the default queue and a single worker process.
set -eu
mkdir -p app/Jobs config tests/Feature
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0", "laravel/boost": "*" } }
JSON
cat > Procfile <<'TXT'
web: php artisan octane:start --host=0.0.0.0
worker: php artisan queue:work redis --queue=default
TXT
cat > config/queue.php <<'PHP'
<?php

return [
    'default' => env('QUEUE_CONNECTION', 'redis'),
    'connections' => [
        'redis' => ['driver' => 'redis', 'connection' => 'queue', 'queue' => 'default', 'retry_after' => 120],
    ],
];
PHP
cat > app/Jobs/SendWeeklyNewsletter.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

// Dispatched once per subscriber every Monday, about 40,000 jobs on the default queue.
final class SendWeeklyNewsletter implements ShouldQueue
{
    use Queueable;

    public function __construct(public int $subscriberId) {}

    public function handle(): void {}
}
PHP
