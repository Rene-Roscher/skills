#!/usr/bin/env bash
set -euo pipefail
mkdir -p app/Jobs app/Http/Controllers config
cat > config/queue.php <<'PHP'
<?php
return [
    'default' => 'redis',
    'connections' => [
        'redis' => ['driver' => 'redis', 'queue' => 'default', 'retry_after' => 90, 'after_commit' => false],
    ],
];
PHP
cat > app/Jobs/SendReminderSms.php <<'PHP'
<?php
namespace App\Jobs;

use App\Models\Booking;
use App\Services\SmsGateway;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class SendReminderSms implements ShouldQueue
{
    use Queueable;

    public $tries = 3;
    public $timeout = 120;

    public function __construct(public int $bookingId) {}

    public function handle(SmsGateway $sms): void
    {
        $booking = Booking::findOrFail($this->bookingId);
        $sms->send($booking->customer->phone, "Reminder: your booking starts at {$booking->starts_at}");
        $booking->customer->organization->decrement('sms_credits');
    }
}
PHP
cat > app/Http/Controllers/BookingController.php <<'PHP'
<?php
namespace App\Http\Controllers;

use App\Jobs\SendReminderSms;
use App\Models\Booking;
use Illuminate\Support\Facades\DB;

class BookingController
{
    public function store()
    {
        return DB::transaction(function () {
            $booking = Booking::create(request()->only('starts_at', 'customer_id'));
            SendReminderSms::dispatch($booking->id)->delay($booking->starts_at->subDay());
            return $booking;
        });
    }
}
PHP
