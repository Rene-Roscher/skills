#!/bin/sh
# Invoicing app: webhook dedupe catches a unique violation inside a transaction.
set -eu
d=app/Domains/Invoicing
mkdir -p "$d/Services" "$d/Models" tests/Feature/Invoicing
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0" } }
JSON
cat > phpunit.xml <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<phpunit bootstrap="vendor/autoload.php" colors="true">
    <testsuites><testsuite name="Feature"><directory>tests/Feature</directory></testsuite></testsuites>
    <php>
        <env name="DB_CONNECTION" value="sqlite"/>
        <env name="DB_DATABASE" value=":memory:"/>
    </php>
</phpunit>
XML
cat > phpunit.pg.xml <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<phpunit bootstrap="vendor/autoload.php" colors="true">
    <testsuites><testsuite name="Feature"><directory>tests/Feature</directory></testsuite></testsuites>
    <php>
        <server name="DB_CONNECTION" value="pgsql"/>
        <server name="DB_DATABASE" value="invoicing_test"/>
    </php>
</phpunit>
XML
cat > "$d/Models/WebhookReceipt.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Models;

use Illuminate\Database\Eloquent\Model;

final class WebhookReceipt extends Model
{
    protected $fillable = ['provider_event_id', 'payload'];

    protected function casts(): array
    {
        return ['payload' => 'array'];
    }
}
PHP
cat > "$d/Services/RecordPaymentWebhook.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Services;

use App\Domains\Invoicing\Models\WebhookReceipt;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;

final class RecordPaymentWebhook
{
    public function execute(string $eventId, array $payload): bool
    {
        return DB::transaction(function () use ($eventId, $payload): bool {
            try {
                WebhookReceipt::create(['provider_event_id' => $eventId, 'payload' => $payload]);
            } catch (QueryException) {
                // unique index on provider_event_id: duplicate delivery
            }

            $receipt = WebhookReceipt::where('provider_event_id', $eventId)->firstOrFail();

            return $receipt->wasRecentlyCreated;
        });
    }
}
PHP
cat > tests/Feature/Invoicing/RecordPaymentWebhookTest.php <<'PHP'
<?php

declare(strict_types=1);

use App\Domains\Invoicing\Services\RecordPaymentWebhook;

it('records a duplicate delivery once', function (): void {
    $service = app(RecordPaymentWebhook::class);

    $service->execute('evt_1', ['amount' => 1200]);
    $service->execute('evt_1', ['amount' => 1200]);

    expect(\App\Domains\Invoicing\Models\WebhookReceipt::count())->toBe(1);
});
PHP
