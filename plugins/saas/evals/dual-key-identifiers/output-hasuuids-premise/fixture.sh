#!/bin/sh
set -eu
mkdir -p app/Models vendor/laravel/framework/src/Illuminate/Database/Eloquent/Concerns
cat > composer.json <<'EOF'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" } }
EOF
cat > composer.lock <<'EOF'
{ "packages": [ { "name": "laravel/framework", "version": "v12.0.0" } ] }
EOF
cat > vendor/laravel/framework/src/Illuminate/Database/Eloquent/Concerns/HasUuids.php <<'EOF'
<?php

namespace Illuminate\Database\Eloquent\Concerns;

use Illuminate\Support\Str;

trait HasUuids
{
    use HasUniqueStringIds;

    /**
     * Generate a new unique key for the model.
     */
    public function newUniqueId()
    {
        return (string) Str::uuid7();
    }
}
EOF
cat > vendor/laravel/framework/src/Illuminate/Database/Eloquent/Concerns/HasVersion4Uuids.php <<'EOF'
<?php

namespace Illuminate\Database\Eloquent\Concerns;

use Illuminate\Support\Str;

trait HasVersion4Uuids
{
    use HasUuids;

    /**
     * Generate a new UUID (version 4) for the model.
     */
    public function newUniqueId()
    {
        return (string) Str::orderedUuid();
    }
}
EOF
cat > app/Models/Customer.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Customer extends Model
{
    protected $fillable = ['name', 'email'];
}
EOF
