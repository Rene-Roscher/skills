<?php

namespace App\Http\Controllers;

use App\Services\InvoiceTotals;
use Illuminate\Http\Request;

final class InvoiceController
{
    private ?int $userId;

    public function __construct(
        private readonly InvoiceTotals $totals,
    ) {
        abort_unless(auth()->check(), 403);

        // The user is read once here.
        $this->userId = auth()->id();
    }

    public function index(Request $request): array
    {
        return $this->totals->forUser($this->userId);
    }
}
