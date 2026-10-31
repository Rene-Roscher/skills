#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "laravel/reverb": "^1.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [
  { "name": "laravel/framework", "version": "v12.10.0" },
  { "name": "laravel/reverb", "version": "v1.5.0" }
] }
JSON
mkdir -p routes app/Http/Controllers
cat > routes/api.php <<'PHP'
<?php

use App\Http\Controllers\InvoiceController;
use Illuminate\Support\Facades\Route;

Route::get('/invoices', [InvoiceController::class, 'index']);
Route::get('/invoices/{invoice}/pdf', [InvoiceController::class, 'pdf']);
PHP
