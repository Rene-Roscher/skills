#!/bin/sh
set -eu
mkdir -p app/Http/Controllers app/Billing database/migrations
cat > composer.json <<'JSON'
{ "name": "example/project-tool", "require": { "php": "^8.4", "laravel/framework": "^12.0" } }
JSON
cat > app/Billing/PaymentProvider.php <<'PHP'
<?php

namespace App\Billing;

interface PaymentProvider
{
    /** Returns ['id' => string, 'status' => string, 'amount' => int, 'currency' => string, 'metadata' => array]. */
    public function fetchPayment(string $id): array;
}
PHP
cat > app/Http/Controllers/PaymentWebhookController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Billing\PaymentProvider;
use Illuminate\Http\Request;

class PaymentWebhookController
{
    // The provider POSTs only the payment id.
    public function __invoke(Request $request, PaymentProvider $provider)
    {
        $id = (string) $request->input('id');

        // TODO: dedup

        return response()->noContent();
    }
}
PHP
cat > database/migrations/2026_01_01_000000_create_webhook_events_table.php <<'PHP'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('webhook_events', function (Blueprint $table) {
            $table->id();
            $table->string('provider');
            $table->string('external_id');
            $table->timestamps();
        });
    }
};
PHP
