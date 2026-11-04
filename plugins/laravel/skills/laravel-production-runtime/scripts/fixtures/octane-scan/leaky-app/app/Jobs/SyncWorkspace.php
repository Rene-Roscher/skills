<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

final class SyncWorkspace implements ShouldQueue
{
    use Queueable;

    public function __construct(public readonly int $workspaceId)
    {
    }

    public function handle(): void
    {
        $workspace = \App\Models\Workspace::query()->findOrFail($this->workspaceId);
        app()->instance('current_workspace', $workspace);

        $this->sync($workspace);
    }

    private function sync(object $workspace): void
    {
    }
}
