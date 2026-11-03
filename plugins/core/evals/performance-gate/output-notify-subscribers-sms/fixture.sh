#!/bin/sh
set -eu
mkdir -p app/Jobs
cat > app/Jobs/NotifySubscribers.php <<'PHP'
<?php

namespace App\Jobs;

use App\Models\Announcement;
use App\Models\Subscriber;
use App\Services\Sms;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class NotifySubscribers implements ShouldQueue
{
    use Queueable;

    public int $tries = 5;

    public function __construct(public Announcement $announcement) {}

    public function handle(Sms $sms): void
    {
        $subscribers = Subscriber::where('tenant_id', $this->announcement->tenant_id)->get();

        foreach ($subscribers as $subscriber) {
            $sms->send($subscriber->phone, $this->announcement->title);
        }
    }
}
PHP
