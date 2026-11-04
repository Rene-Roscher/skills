<?php

namespace App\Http\Controllers;

use App\Services\QuotaService;

final class QuotaController
{
    public function __construct(private readonly QuotaService $quotas)
    {
    }
}
