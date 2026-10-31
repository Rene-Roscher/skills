#!/bin/sh
set -eu
mkdir -p config
cat > composer.json <<'JSON'
{ "name": "example/invoicing-app", "require": { "php": "^8.4", "laravel/framework": "^12.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" }, { "name": "symfony/mailer", "version": "v7.4.6" } ] }
JSON
cat > config/mail.php <<'PHP'
<?php

return [
    'default' => env('MAIL_MAILER', 'postmark'),

    'mailers' => [
        'postmark' => [
            'transport' => 'postmark',
        ],
        'resend' => [
            'transport' => 'resend',
        ],
        'log' => [
            'transport' => 'log',
            'channel' => env('MAIL_LOG_CHANNEL'),
        ],
    ],

    'from' => [
        'address' => env('MAIL_FROM_ADDRESS', 'billing@example.com'),
        'name' => env('MAIL_FROM_NAME', 'Invoicing'),
    ],
];
PHP
