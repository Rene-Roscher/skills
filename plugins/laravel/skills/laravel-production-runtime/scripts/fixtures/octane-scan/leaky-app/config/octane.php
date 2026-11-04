<?php

use Laravel\Socialite\Contracts\Factory;

return [
    'flush' => [
        'legacy_tenant',
        Factory::class,
        'current_project',
    ],
];
