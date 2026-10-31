#!/bin/sh
set -eu
mkdir -p config docs/adr
cat > composer.json <<'EOF'
{ "require": { "php": "^8.3", "laravel/framework": "^12.0", "spatie/laravel-permission": "^6.0" } }
EOF
cat > config/permission.php <<'EOF'
<?php

return [
    // Teams mode is off in this project for now.
    'teams' => false,
    'cache' => [
        'expiration_time' => \DateInterval::createFromDateString('24 hours'),
    ],
];
EOF
