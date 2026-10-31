#!/bin/sh
set -eu
mkdir -p app/Http/Controllers database/migrations
cat > app/Http/Controllers/ActivityController.php <<'EOF'
<?php

namespace App\Http\Controllers;

use App\Http\Resources\ActivityResource;
use App\Models\Organization;

class ActivityController extends Controller
{
    public function index(Organization $organization)
    {
        $activities = $organization->activities()->latest()->paginate(50);

        return ActivityResource::collection($activities);
    }
}
EOF
cat > database/migrations/2026_01_12_000000_create_activities_table.php <<'EOF'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('activities', function (Blueprint $table) {
            $table->id();
            $table->string('public_id', 21)->unique();
            $table->foreignId('organization_id')->constrained();
            $table->string('type');
            $table->json('properties');
            $table->timestamps();
            $table->index(['organization_id', 'created_at']);
        });
    }
};
EOF
