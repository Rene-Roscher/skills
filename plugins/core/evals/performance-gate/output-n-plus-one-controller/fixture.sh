#!/bin/sh
set -eu
mkdir -p app/Http/Controllers
cat > app/Http/Controllers/ProjectController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Models\Project;
use Illuminate\Http\Request;

class ProjectController extends Controller
{
    public function index(Request $request)
    {
        $projects = Project::where('tenant_id', $request->user()->tenant_id)->get();

        $rows = [];
        foreach ($projects as $project) {
            $rows[] = [
                'id' => $project->public_id,
                'name' => $project->name,
                'owner' => $project->owner->name,
                'open_tasks' => $project->tasks()->where('done', false)->count(),
            ];
        }

        return inertia('Projects/Index', ['projects' => $rows]);
    }
}
PHP
