#!/bin/sh
set -eu
mkdir -p database/migrations app/Services
cat > database/migrations/2024_02_01_000000_create_projects_tables.php <<'PHP'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('projects', function (Blueprint $table) {
            $table->id();
            $table->string('public_id', 21)->unique();
            $table->foreignId('organization_id')->constrained();
            $table->string('name');
        });
        Schema::create('tasks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained();
            $table->foreignId('project_id')->constrained();
            $table->string('title');
        });
        Schema::create('comments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained();
            $table->foreignId('task_id')->constrained();
            $table->text('body');
        });
        Schema::create('project_members', function (Blueprint $table) {
            $table->foreignId('project_id')->constrained();
            $table->foreignId('user_id')->constrained();
            $table->primary(['project_id', 'user_id']);
        });
    }
};
PHP
cat > app/Services/ProjectLimits.php <<'PHP'
<?php

namespace App\Services;

use App\Models\Organization;

class ProjectLimits
{
    /** Plan limit check for creating (or receiving) one more project. */
    public function canCreateProject(Organization $organization): bool
    {
        return app(Entitlements::class)->remaining($organization, 'projects') > 0;
    }
}
PHP
