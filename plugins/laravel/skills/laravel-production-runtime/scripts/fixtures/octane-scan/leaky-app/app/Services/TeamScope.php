<?php

namespace App\Services;

final class TeamScope
{
    private ?string $team;

    public function __construct()
    {
        $this->team = request()->route('team');
    }
}
