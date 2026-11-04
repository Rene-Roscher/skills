<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

final class BindProject
{
    public function handle(Request $request, Closure $next): mixed
    {
        app()->forgetInstance('current_project');

        if ($request->route('project') === null) {
            return $next($request);
        }

        app()->instance('current_project', $request->route('project'));

        return $next($request);
    }
}
