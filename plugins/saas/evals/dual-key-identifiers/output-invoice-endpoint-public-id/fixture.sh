#!/bin/sh
set -eu
mkdir -p app/Models database/migrations routes
cat > composer.json <<'EOF'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0" } }
EOF
cat > app/Models/Organization.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Organization extends Model
{
    public function invoices(): HasMany
    {
        return $this->hasMany(Invoice::class);
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
cat > app/Models/Invoice.php <<'EOF'
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Invoice extends Model
{
    protected $fillable = ['number', 'total_cents', 'customer_id'];

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }
}
EOF
cat > database/migrations/2026_01_10_000000_create_invoices_table.php <<'EOF'
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('invoices', function (Blueprint $table) {
            $table->id();
            $table->string('public_id', 21)->unique();
            $table->foreignId('organization_id')->constrained();
            $table->foreignId('customer_id')->constrained();
            $table->string('number');
            $table->bigInteger('total_cents');
            $table->timestamps();
        });
    }
};
EOF
cat > routes/api.php <<'EOF'
<?php

use Illuminate\Support\Facades\Route;

Route::prefix('v1')->middleware('auth:sanctum')->group(function () {
    // invoice routes go here
});
EOF
