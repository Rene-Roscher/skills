#!/bin/sh
# Minimal Laravel-shaped project for a project-management tool. No vendor code is needed.
set -eu
mkdir -p app/Models/Concerns app/Support app/Domains/Projects/Models routes tests/Feature
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" },
  "require-dev": { "pestphp/pest": "^4.0", "laravel/boost": "*" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" } ],
  "packages-dev": [ { "name": "pestphp/pest", "version": "v4.3.2" }, { "name": "laravel/boost", "version": "v1.0.0" } ] }
JSON
cat > app/Support/PublicId.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Support;

final class PublicId
{
    public const LENGTH = 21;

    public static function generate(): string
    {
        $alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
        $id = '';
        while (strlen($id) < self::LENGTH) {
            $value = ord(random_bytes(1)) & 63;
            if ($value < 62) {
                $id .= $alphabet[$value];
            }
        }

        return $id;
    }
}
PHP
cat > app/Models/Concerns/HasPublicId.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Models\Concerns;

use App\Support\PublicId;
use Illuminate\Database\Eloquent\Model;

trait HasPublicId
{
    public static function bootHasPublicId(): void
    {
        static::creating(function (Model $model): void {
            $model->public_id ??= PublicId::generate();
        });
    }

    public function getRouteKeyName(): string
    {
        return 'public_id';
    }
}
PHP
cat > app/Models/User.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Models;

use App\Models\Concerns\HasPublicId;
use Illuminate\Foundation\Auth\User as Authenticatable;

final class User extends Authenticatable
{
    use HasPublicId;

    protected $fillable = ['name', 'email'];
}
PHP
cat > app/Domains/Projects/Models/Project.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Projects\Models;

use App\Models\Concerns\HasPublicId;
use App\Models\User;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

final class Project extends Model
{
    use HasPublicId;

    protected $fillable = ['name', 'budget_cents'];

    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }
}
PHP
cat > routes/api.php <<'PHP'
<?php

declare(strict_types=1);

use Illuminate\Support\Facades\Route;

Route::prefix('v1')->middleware('auth:sanctum')->group(function (): void {
    // API routes
});
PHP
cat > tests/TestCase.php <<'PHP'
<?php

declare(strict_types=1);

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    // setUp() pushes the ID-leak guard middleware; it checks every feature-test response.
}
PHP
cat > tests/Pest.php <<'PHP'
<?php

declare(strict_types=1);

pest()->extend(Tests\TestCase::class)
    ->use(Illuminate\Foundation\Testing\RefreshDatabase::class)
    ->in('Feature');
PHP
