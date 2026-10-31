#!/bin/sh
set -eu
mkdir -p app/Enums app/Services app/Models
cat > app/Enums/Permission.php <<'EOF'
<?php

namespace App\Enums;

enum Permission: string
{
    case BookingsView = 'bookings.view';
    case BookingsCancel = 'bookings.cancel';
    case RoomsManage = 'rooms.manage';
    case ReportsView = 'reports.view';
    case TokensManage = 'tokens.manage';
    case BillingManage = 'billing.manage';
}
EOF
cat > app/Services/EffectivePermissions.php <<'EOF'
<?php

namespace App\Services;

use App\Enums\Permission;
use App\Models\Member;

class EffectivePermissions
{
    /**
     * Effective permissions of a member in their organization:
     * the owner holds every permission, an inactive member holds none,
     * everyone else holds the union of their roles' permissions.
     *
     * @return list<Permission>
     */
    public function for(Member $member): array
    {
        if ($member->isOwner()) {
            return Permission::cases();
        }
        if (! $member->is_active) {
            return [];
        }

        return $member->roles
            ->flatMap(fn ($role) => $role->permissions)
            ->unique()
            ->map(fn (string $value) => Permission::from($value))
            ->values()
            ->all();
    }
}
EOF
cat > app/Models/ApiToken.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ApiToken extends Model
{
    protected $fillable = ['name', 'abilities', 'expires_at'];

    protected $casts = ['abilities' => 'array', 'expires_at' => 'datetime'];
}
EOF
