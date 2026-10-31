#!/bin/sh
set -eu
mkdir -p app/Models app/Support app/Jobs tests/Feature
cat > app/Models/Organization.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Organization extends Model
{
    use SoftDeletes;

    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }

    public function usageRecords(): HasMany
    {
        return $this->hasMany(UsageRecord::class);
    }

    public function isScheduledForDeletion(): bool
    {
        return $this->deletion_scheduled_at !== null;
    }
}
EOF
cat > app/Models/UsageRecord.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UsageRecord extends Model
{
    protected $casts = ['recorded_at' => 'datetime'];
}
EOF
cat > app/Support/CurrentOrganization.php <<'EOF'
<?php

namespace App\Support;

use App\Models\Organization;

/**
 * Holds the organization bound by the tenant middleware for the current request.
 */
class CurrentOrganization
{
    private ?Organization $organization = null;

    public function set(Organization $organization): void
    {
        $this->organization = $organization;
    }

    public function get(): Organization
    {
        return $this->organization ?? throw new \RuntimeException('No organization bound.');
    }
}
EOF
