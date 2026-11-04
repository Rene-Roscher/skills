#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p app/Domains/Orders/Models app/Domains/Orders/Contracts app/Domains/Billing/Services tests/Arch docs
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0" } }
JSON
cat > app/Domains/Orders/Models/Order.php <<'PHP'
<?php

namespace App\Domains\Orders\Models;

use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    protected $table = 'orders';
}
PHP
cat > app/Domains/Billing/Services/CreateInvoiceService.php <<'PHP'
<?php

namespace App\Domains\Billing\Services;

final class CreateInvoiceService
{
    public function execute(string $orderId): void
    {
        // needs the order total
    }
}
PHP
cat > tests/Arch/ContextsTest.php <<'PHP'
<?php

arch('orders models stay in orders')
    ->expect('App\Domains\Orders\Models')
    ->toOnlyBeUsedIn('App\Domains\Orders');
PHP
cat > docs/CONTEXT-MAP.md <<'MD'
# Context map

| upstream | downstream | relationship | mechanism | contract | enforced by |
|---|---|---|---|---|---|
| Catalog | Orders | customer/supplier | call `ProductQuery` | app/Domains/Catalog/Contracts | tests/Arch/ContextsTest.php |
MD
cat > docs/GLOSSARY.md <<'MD'
| term | aliases | meaning in this project | not to confuse with | source |
|---|---|---|---|---|
| Order | purchase | a customer's confirmed basket with lines and a total | Invoice | product team |
| Invoice | bill | the billing document created for an Order | Order | finance |
MD
