<?php

namespace App\Services;

final class CurrentAccount
{
    public readonly ?int $id;

    public function __construct()
    {
        // Safe: bound with scoped(), rebuilt for every request and job.
        $this->id = auth()->user()?->getAuthIdentifier();
    }
}
