#!/bin/sh
# Multi-tenant invoicing app: products belong to a team and carry a public ID.
set -eu
d=app/Domains/Invoicing
mkdir -p "$d/Models" "$d/FormRequests" app/Models
cat > composer.json <<'JSON'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" }, "require-dev": { "pestphp/pest": "^4.0", "laravel/boost": "*" } }
JSON
cat > "$d/Models/Product.php" <<'PHP'
<?php

declare(strict_types=1);

namespace App\Domains\Invoicing\Models;

use App\Models\Concerns\HasPublicId;
use Illuminate\Database\Eloquent\Model;

// Columns: id (bigint), public_id (char 21, unique), team_id (bigint), name, price_cents.
final class Product extends Model
{
    use HasPublicId;

    protected $fillable = ['name', 'price_cents'];
}
PHP
cat > app/Models/User.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;

// The team the user is working in is stored in current_team_id.
final class User extends Authenticatable
{
    protected $fillable = ['name', 'email'];
}
PHP
