#!/bin/sh
set -eu
mkdir -p tests/e2e routes config
cat > playwright.config.ts <<'TS'
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: 'tests/e2e',
  use: { baseURL: 'http://127.0.0.1:8000' },
  webServer: {
    command: 'php artisan serve --port=8000',
    url: 'http://127.0.0.1:8000',
    reuseExistingServer: true,
  },
})
TS
cat > tests/e2e/notes.spec.ts <<'TS'
import { test, expect } from '@playwright/test'

for (let i = 0; i < 8; i++) {
  test(`creates note ${i}`, async ({ page }) => {
    await page.goto('/notes/new')
    await page.getByTestId('note-body').fill(`Note ${i}`)
    await page.getByTestId('note-save').click()
    await expect(page.getByTestId('note-created')).toBeVisible()
  })
}
TS
cat > routes/web.php <<'PHP'
<?php

use App\Http\Controllers\NoteController;
use Illuminate\Support\Facades\Route;

Route::get('/notes/new', [NoteController::class, 'create']);
Route::post('/notes', [NoteController::class, 'store'])->middleware('throttle:notes');
PHP
cat > config/cache.php <<'PHP'
<?php

return [
    'default' => env('CACHE_STORE', 'database'),
];
PHP
mkdir -p app/Providers
cat > app/Providers/AppServiceProvider.php <<'PHP'
<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        RateLimiter::for('notes', fn (Request $request) => Limit::perHour(20)->by($request->ip()));
    }
}
PHP
cat > .env <<'ENV'
APP_URL=http://127.0.0.1:8000
DB_CONNECTION=pgsql
DB_DATABASE=notes_dev
CACHE_STORE=database
ENV
