#!/bin/sh
set -eu
mkdir -p routes config resources/js/pages
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "inertiajs/inertia-laravel": "^2.0" } }
JSON
cat > package.json <<'JSON'
{ "private": true, "type": "module", "dependencies": { "@inertiajs/vue3": "^2.0.0", "vue": "^3.5.0" } }
JSON
cat > routes/web.php <<'PHP'
<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::middleware('auth')->group(function () {
    Route::get('/dashboard', fn () => Inertia::render('Dashboard'))->name('dashboard');
    Route::get('/bookings', fn () => Inertia::render('Bookings/Index'))->name('bookings.index');
});
PHP
cat > config/inertia.php <<'PHP'
<?php

return ['ssr' => ['enabled' => false]];
PHP
cat > resources/js/pages/Dashboard.vue <<'VUE'
<script setup lang="ts">
defineProps<{ bookingsToday: number }>()
</script>

<template>
  <h1>Today</h1>
</template>
VUE
