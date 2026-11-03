#!/bin/sh
set -eu
mkdir -p app/Listeners app/Models config
cat > app/Listeners/HandlePlanChanged.php <<'PHP'
<?php

namespace App\Listeners;

use App\Events\PlanChanged;

class HandlePlanChanged
{
    public function handle(PlanChanged $event): void
    {
        // $event->organization, $event->oldPlan, $event->newPlan
        // TODO: enforce the new plan's seat limit
    }
}
PHP
cat > app/Models/Membership.php <<'PHP'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

/**
 * @property int $organization_id
 * @property int $user_id
 * @property string $status  active|deactivated
 */
class Membership extends Model
{
    protected $fillable = ['user_id', 'status'];
}
PHP
cat > config/plans.php <<'PHP'
<?php

// seats = members in addition to the organization owner
return [
    'starter' => ['seats' => 2],
    'business' => ['seats' => 10],
];
PHP
