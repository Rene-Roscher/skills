#!/bin/sh
# Booking system: the controller hands the raw input string to Eloquent.
set -eu
d=app/Domains/Bookings
mkdir -p "$d/Controllers" "$d/FormRequests" "$d/Models" config tests/Feature
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0" } }
JSON
cat > config/database.php <<'PHP'
<?php

return [
    'default' => env('DB_CONNECTION', 'pgsql'),
    'connections' => [
        'pgsql' => [
            'driver' => 'pgsql',
            'host' => env('DB_HOST', '127.0.0.1'),
            'database' => env('DB_DATABASE', 'bookings'),
            'username' => env('DB_USERNAME', 'bookings'),
            'password' => env('DB_PASSWORD', ''),
            'timezone' => 'UTC',
        ],
    ],
];
PHP
cat > "$d/Models/Booking.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Bookings\Models;

use Illuminate\Database\Eloquent\Model;

final class Booking extends Model
{
    protected $fillable = ['room_id', 'starts_at', 'ends_at'];

    protected function casts(): array
    {
        return ['starts_at' => 'datetime', 'ends_at' => 'datetime'];
    }
}
PHP
cat > "$d/FormRequests/StoreBookingRequest.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Bookings\FormRequests;

use Illuminate\Foundation\Http\FormRequest;

final class StoreBookingRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'room_id' => ['required', 'integer'],
            'starts_at' => ['required', 'date'],
            'ends_at' => ['required', 'date', 'after:starts_at'],
        ];
    }
}
PHP
cat > "$d/Controllers/BookingController.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Bookings\Controllers;

use App\Domains\Bookings\FormRequests\StoreBookingRequest;
use App\Domains\Bookings\Models\Booking;
use Illuminate\Http\JsonResponse;

final class BookingController
{
    public function store(StoreBookingRequest $request): JsonResponse
    {
        $booking = Booking::create([
            'room_id' => $request->validated('room_id'),
            'starts_at' => $request->validated('starts_at'),
            'ends_at' => $request->validated('ends_at'),
        ]);

        return response()->json(['starts_at' => $booking->starts_at->toIso8601String()], 201);
    }
}
PHP
