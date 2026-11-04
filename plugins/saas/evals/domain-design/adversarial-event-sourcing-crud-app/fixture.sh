#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" } }
JSON
mkdir -p database/migrations app/Http/Controllers routes
for t in customers invoices invoice_lines; do
  cat > "database/migrations/2026_01_01_000000_create_${t}_table.php" <<PHP
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('${t}', function (Blueprint \$table) {
            \$table->id();
            \$table->string('name');
            \$table->timestamps();
        });
    }
};
PHP
done
cat > routes/web.php <<'PHP'
<?php

use App\Http\Controllers\InvoiceController;
use Illuminate\Support\Facades\Route;

Route::resource('invoices', InvoiceController::class);
PHP
