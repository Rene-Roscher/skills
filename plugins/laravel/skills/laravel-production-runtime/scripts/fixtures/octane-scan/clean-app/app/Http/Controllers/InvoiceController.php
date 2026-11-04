<?php

namespace App\Http\Controllers;

use App\Services\InvoiceTotals;
use App\Services\VisibleProjects;
use Illuminate\Http\Request;

final class InvoiceController
{
    public function __construct(private readonly InvoiceTotals $totals)
    {
        $this->middleware(function (Request $request, $next) {
            abort_unless($request->user() !== null, 403);

            return $next($request);
        });
    }

    public function index(Request $request, VisibleProjects $projects): array
    {
        return $this->totals->forUser((int) $request->user()->id) + $projects->forCurrentUser($request);
    }
}
