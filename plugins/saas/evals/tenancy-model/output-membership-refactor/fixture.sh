#!/bin/sh
set -eu
mkdir -p database/migrations app/Models
cat > database/migrations/2024_01_01_000000_create_organizations_and_users.php <<'PHP'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('organizations', function (Blueprint $table) {
            $table->id();
            $table->string('public_id', 21)->unique();
            $table->string('name');
            $table->timestamps();
        });

        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained();
            $table->string('role')->default('member'); // 'admin' or 'member'
            $table->string('email')->unique();
            $table->string('password');
            $table->timestamps();
        });
    }
};
PHP
cat > app/Models/User.php <<'PHP'
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;

class User extends Authenticatable
{
    public function organization()
    {
        return $this->belongsTo(Organization::class);
    }

    public function isAdmin(): bool
    {
        return $this->role === 'admin';
    }
}
PHP
