<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

final class BindWorkspace
{
    public function handle(Request $request, Closure $next): mixed
    {
        app()->forgetInstance('current_workspace');

        if ($request->user() === null) {
            return $next($request);
        }

        app()->instance('current_workspace', $request->user()->workspace);

        return $next($request);
    }
}
