# Laravel notes

Load when the project uses Laravel. Checked against the Laravel 12 docs and laravel/framework `12.x` source on
2026-10-31; re-check for the installed version. Worker-state rules (Octane flush lists, singletons, request stamps)
live in `laravel-production-runtime`; syntax for bindings and validation lives in the Laravel docs and in Laravel
Boost's guidelines.

## Tenant middleware

- First statement: forget the previous binding (`app()->forgetInstance(...)` or the equivalent on your holder),
  before any early return for guests or users without a tenant.
- Resolve the tenant from the route parameter, check active membership, then bind.
- The accessor that reads the bound tenant throws or denies when nothing is bound. No `?? $user->tenants()->first()`.
- Order matters. Laravel's default middleware priority runs `AuthenticatesRequests` before `SubstituteBindings`,
  and `SubstituteBindings` before `Authorize` (`$middlewarePriority` in
  https://github.com/laravel/framework/blob/12.x/src/Illuminate/Foundation/Http/Kernel.php, verified 2026-10-31).
  A tenant middleware outside that list keeps its place in the route's stack, often after the group's
  `SubstituteBindings`, so a global tenant scope is not active yet when route models resolve. Resolve tenant
  children through the tenant relation, or move the tenant middleware ahead of bindings with
  `prependToPriorityList(SubstituteBindings::class, YourTenantMiddleware::class)`, which keeps it after
  authentication.

## Resolving resources

- Nested routes: `scopeBindings()` scopes the child to the parent, and `withoutScopedBindings()` turns it off
  (https://laravel.com/docs/12.x/routing). The parent segment itself still needs the membership check, and scoping
  does not replace the permission check.
- Controllers that take a raw public ID resolve with `$workspace->projects()->where('public_id', $id)->firstOrFail()`.
- A policy can answer 404 instead of 403 with `Response::denyAsNotFound()` (https://laravel.com/docs/12.x/authorization).
  Inside a tenant-scoped lookup the foreign case never reaches the policy, which is the stronger design.

## Validation of referenced IDs

- `exists` rules for references are scoped to the tenant, for example `Rule::exists('projects', 'public_id')` with a
  `where` on the tenant column. An unscoped `exists:projects,public_id` accepts any tenant's project.
- For arrays, validate that the count of matching rows inside the tenant equals the count of distinct submitted
  IDs, in one query.

## Mass assignment

- Tenant foreign keys and current-tenant pointers stay out of `$fillable`. Set them from the bound tenant in the
  service or through the relation (`$workspace->projects()->create(...)`).

## Jobs

- `__construct(public int $workspaceId, public int $projectId)` with scalars.
- In `handle()`: resolve through `Workspace::find($this->workspaceId)`, stop when it is missing, suspended or pending
  deletion, then resolve the project through the workspace.
- Laravel Context hydrates into jobs (https://laravel.com/docs/12.x/context). Keep tenant IDs out of it, or use them
  only for log fields.

## Cache

- `Cache::tags(["workspace:{$id}", "workspace:{$id}:dashboard"])->remember($key . ':' . $viewerFragment, ...)`.
- Invalidate with `Cache::tags(["workspace:{$id}:dashboard"])->flush()`. A `Cache::forget($key)` misses tagged
  entries. Tags are not supported on the `file`, `dynamodb` and `database` drivers
  (https://laravel.com/docs/12.x/cache).

## Broadcasting

- Register channels with public IDs: `Broadcast::channel('project.{publicId}', ...)`.
- Test the callbacks directly by resolving them from the broadcaster and invoking them; with the `null` driver the
  HTTP auth endpoint never runs them (`NullBroadcaster::auth()` is empty in `12.x`,
  https://github.com/laravel/framework/blob/12.x/src/Illuminate/Broadcasting/Broadcasters/NullBroadcaster.php).

## Global scopes

- If a visibility feature uses a global scope, give it a named opt-out method and make the structural guard match
  both that method and `withoutGlobalScope(...)` / `withoutGlobalScopes()`.
