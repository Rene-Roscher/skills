#!/bin/sh
set -eu
mkdir -p app/Http/Controllers config
cat > app/Http/Controllers/DashboardController.php <<'EOF'
<?php

namespace App\Http\Controllers;

use App\Models\Task;
use App\Models\Workspace;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    public function show(Request $request, Workspace $workspace)
    {
        $member = $request->user()->membershipIn($workspace);
        $projectIds = $member->visibleProjectIds();

        return response()->json([
            'open_tasks' => Task::whereIn('project_id', $projectIds)->where('status', 'open')->count(),
            'overdue_tasks' => Task::whereIn('project_id', $projectIds)->where('due_at', '<', now())->count(),
        ]);
    }
}
EOF
cat > config/cache.php <<'EOF'
<?php

return [
    'default' => env('CACHE_STORE', 'redis'),
];
EOF
