#!/bin/sh
# Booking system with one DTO and a stub of the installed Pest expectation API (method names only).
set -eu
mkdir -p app/Domains/Bookings/DTOs tests/Arch vendor/pestphp/pest/src
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" } ], "packages-dev": [ { "name": "pestphp/pest", "version": "v4.3.2" } ] }
JSON
cat > app/Domains/Bookings/DTOs/BookingData.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Bookings\DTOs;

final readonly class BookingData
{
    public function __construct(
        public string $roomId,
        public string $startsAt,
        public int $nights,
    ) {}
}
PHP
cat > vendor/pestphp/pest/src/Expectation.php <<'PHP'
<?php

// Fixture stub: the arch expectation names available in the installed Pest version.

namespace Pest;

final class Expectation
{
    public function toBeFinal() {}
    public function toBeReadonly() {}
    public function toBeEnums() {}
    public function toBeClasses() {}
    public function toBeTraits() {}
    public function toExtend(string $class) {}
    public function toHaveSuffix(string $suffix) {}
    public function toHaveMethod(array|string $method) {}
    public function toOnlyBeUsedIn(array|string $targets) {}
    public function toUseStrictTypes() {}
}
PHP
