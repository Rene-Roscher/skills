#!/bin/sh
set -eu
mkdir -p app/Billing
cat > composer.json <<'JSON'
{
    "name": "example/booking-app",
    "require": { "php": "^8.4", "laravel/framework": "^12.0" },
    "config": { "platform": { "php": "8.4.27" } }
}
JSON
cat > app/Billing/PlanPrice.php <<'PHP'
<?php

namespace App\Billing;

final readonly class PlanPrice
{
    public function __construct(
        public int $netCents,
        public string $currency,
    ) {}
}
PHP
