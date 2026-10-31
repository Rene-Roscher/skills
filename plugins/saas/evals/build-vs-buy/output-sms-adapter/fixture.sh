#!/bin/sh
set -eu
mkdir -p app/Domains/Booking/Models tests
cat > composer.json <<'JSON'
{
    "name": "example/booking-app",
    "require": { "php": "^8.4", "laravel/framework": "^12.0" },
    "require-dev": { "pestphp/pest": "^4.0" },
    "autoload": { "psr-4": { "App\\": "app/" } }
}
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" } ], "packages-dev": [ { "name": "pestphp/pest", "version": "v4.1.0" } ] }
JSON
cat > app/Domains/Booking/Models/Appointment.php <<'PHP'
<?php

namespace App\Domains\Booking\Models;

use Illuminate\Database\Eloquent\Model;

class Appointment extends Model
{
    protected $casts = ['starts_at' => 'immutable_datetime'];
}
PHP
cat > tests/Pest.php <<'PHP'
<?php

uses(Tests\TestCase::class)->in('Feature');
PHP
