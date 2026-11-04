<?php

namespace App\Services;

final class CurrentAccount
{
    public readonly ?int $id;

    public function __construct()
    {
        $this->id = auth()->user()?->getAuthIdentifier();
    }
}
