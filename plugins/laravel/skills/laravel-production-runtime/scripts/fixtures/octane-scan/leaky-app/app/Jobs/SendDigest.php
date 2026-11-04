<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

final class SendDigest implements ShouldQueue
{
    use Queueable;

    public function __construct(public readonly int $userId)
    {
    }

    public function handle(): void
    {
        auth()->loginUsingId($this->userId);
        config(['app.locale' => 'de']);

        try {
            app()->instance('current_project', $this->userId);
        } finally {
            logger()->info('digest sent');
        }
    }
}
