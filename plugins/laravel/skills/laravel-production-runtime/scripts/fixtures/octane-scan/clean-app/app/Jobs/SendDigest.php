<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Auth;

final class SendDigest implements ShouldQueue
{
    use Queueable;

    public function __construct(public readonly int $userId)
    {
    }

    public function handle(): void
    {
        try {
            Auth::loginUsingId($this->userId);
        } finally {
            Auth::logout();
        }
    }
}
