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

        try {
            app()->instance('current_workspace', $workspace);
            $this->sync($workspace);
        } finally {
            app()->forgetInstance('current_workspace');
        }
    }

    private function sync(object $workspace): void
    {
    }
}
