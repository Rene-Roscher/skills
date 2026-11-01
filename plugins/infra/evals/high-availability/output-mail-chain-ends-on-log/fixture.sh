#!/usr/bin/env bash
set -euo pipefail
mkdir -p config
cat > config/mail.php <<'PHP'
<?php

return [
    'default' => env('MAIL_MAILER', 'failover'),

    'mailers' => [
        'primary' => [
            'transport' => 'smtp',
            'host' => 'smtp.mail-a.example.com',
            'port' => 587,
        ],
        'secondary' => [
            'transport' => 'smtp',
            'host' => 'smtp.mail-b.example.net',
            'port' => 587,
        ],
        'log' => [
            'transport' => 'log',
            'channel' => env('MAIL_LOG_CHANNEL'),
        ],
        'failover' => [
            'transport' => 'failover',
            'mailers' => ['primary', 'secondary', 'log'],
            'retry_after' => 60,
        ],
    ],

    'from' => ['address' => 'alerts@example.com', 'name' => 'Booking alerts'],
];
PHP
cat > README.md <<'MD'
# booking-alerts
Sends outage alarms and booking confirmations. Alarms must reach the on-call person even when one mail provider is down.
MD
