#!/bin/sh
set -eu
mkdir -p app/Services app/Http/Controllers
cat > app/Services/Limits.php <<'PHP'
<?php

namespace App\Services;

use App\Models\Organization;

class Limits
{
    private const PLANS = [
        'free' => ['projects' => 3, 'api' => false],
        'pro' => ['projects' => 50, 'api' => true],
    ];

    public function canCreateProject(Organization $organization): bool
    {
        $limit = self::PLANS[$organization->plan]['projects'] ?? 0;

        return $organization->projects()->count() < $limit;
    }

    public function hasApi(Organization $organization): bool
    {
        return $organization->plan === 'pro';
    }
}
PHP
cat > app/Http/Controllers/ProjectController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreProjectRequest;
use App\Services\Limits;

class ProjectController
{
    public function store(StoreProjectRequest $request, Limits $limits)
    {
        $organization = $request->organization();
        abort_unless($limits->canCreateProject($organization), 403, 'Project limit reached');

        return $organization->projects()->create($request->validated());
    }
}
PHP
