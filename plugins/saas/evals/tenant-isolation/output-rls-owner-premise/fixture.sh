#!/bin/sh
set -eu
mkdir -p database/migrations config
cat > database/migrations/2026_02_01_000000_enable_row_level_security.php <<'EOF'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        foreach (['projects', 'tasks', 'comments'] as $table) {
            DB::statement("ALTER TABLE {$table} ENABLE ROW LEVEL SECURITY");
            DB::statement("CREATE POLICY tenant_isolation ON {$table} USING (workspace_id = current_setting('app.workspace_id')::bigint)");
        }
    }
};
EOF
cat > config/database.php <<'EOF'
<?php

return [
    'default' => 'pgsql',
    'connections' => [
        'pgsql' => [
            'driver' => 'pgsql',
            'host' => env('DB_HOST', '127.0.0.1'),
            'database' => env('DB_DATABASE', 'app'),
            // The same role runs migrations and serves the app; it owns every table.
            'username' => env('DB_USERNAME', 'app_owner'),
            'password' => env('DB_PASSWORD', ''),
        ],
    ],
];
EOF
