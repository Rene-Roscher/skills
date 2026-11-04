<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

final class BindWorkspace
{
    public function handle(Request $request, Closure $next): mixed
    {
        if ($request->user() === null) {
            return $next($request);
        }

        $workspace = $request->user()->workspace;

        app()->instance('current_workspace', $workspace);

        return $next($request);
    }
}
