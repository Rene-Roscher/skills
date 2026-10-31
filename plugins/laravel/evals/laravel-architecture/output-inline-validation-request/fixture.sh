#!/bin/sh
# Minimal Laravel-shaped invoicing app with an existing FormRequest convention.
set -eu
d=app/Domains/Invoicing
mkdir -p "$d/Controllers" "$d/FormRequests" "$d/Services" "$d/Models" "$d/DTOs"
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0", "laravel/boost": "*" } }
JSON
cat > "$d/Models/Invoice.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Models;

use Illuminate\Database\Eloquent\Model;

final class Invoice extends Model
{
    protected $fillable = ['customer_reference', 'amount_cents'];
}
PHP
cat > "$d/DTOs/InvoiceData.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\DTOs;

final readonly class InvoiceData
{
    public function __construct(
        public string $customerReference,
        public int $amountCents,
    ) {}
}
PHP
cat > "$d/FormRequests/StoreInvoiceRequest.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\FormRequests;

use Illuminate\Foundation\Http\FormRequest;

final class StoreInvoiceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', \App\Domains\Invoicing\Models\Invoice::class) ?? false;
    }

    public function rules(): array
    {
        return [
            'customer_reference' => ['required', 'string', 'max:64'],
            'amount_cents' => ['required', 'integer', 'min:1'],
        ];
    }
}
PHP
cat > "$d/Services/UpdateInvoiceService.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Services;

use App\Domains\Invoicing\DTOs\InvoiceData;
use App\Domains\Invoicing\Models\Invoice;

final class UpdateInvoiceService
{
    public function execute(Invoice $invoice, InvoiceData $data): Invoice
    {
        $invoice->update([
            'customer_reference' => $data->customerReference,
            'amount_cents' => $data->amountCents,
        ]);

        return $invoice;
    }
}
PHP
cat > "$d/Controllers/InvoiceController.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Controllers;

use App\Domains\Invoicing\DTOs\InvoiceData;
use App\Domains\Invoicing\FormRequests\StoreInvoiceRequest;
use App\Domains\Invoicing\Models\Invoice;
use App\Domains\Invoicing\Services\UpdateInvoiceService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

final class InvoiceController
{
    public function store(StoreInvoiceRequest $request): RedirectResponse
    {
        // creation handled elsewhere
        return back();
    }

    public function update(Request $request, Invoice $invoice, UpdateInvoiceService $service): RedirectResponse
    {
        $service->execute($invoice, new InvoiceData(
            customerReference: (string) $request->input('customer_reference'),
            amountCents: (int) $request->input('amount_cents'),
        ));

        return back();
    }
}
PHP
