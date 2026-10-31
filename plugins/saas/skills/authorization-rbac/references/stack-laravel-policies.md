# Laravel policies and gates

Load when the project uses Laravel policies and gates. Checked against the Laravel 12 docs
(https://laravel.com/docs/12.x/authorization) on 2026-10-31; re-check for the installed version. Syntax for policies,
gates and mass assignment is in the Laravel docs and in Laravel Boost's guidelines. This file keeps the decisions
and traps.

## Base policy

- Every tenant policy extends one base policy. Its `before()` returns false when no tenant is bound or when the
  route-bound subject is outside the tenant or the actor's visible set, and null otherwise so the ability method
  decides.
- It never returns true for staff. Staff work happens on a separate admin surface or through audited
  impersonation.

## The `before()` trap

The docs: "The `before` method of a policy class will not be called if the class doesn't contain a method with a name
matching the name of the ability being checked." A missing method skips the base pre-check without any error.

- Add a method for every ability the app checks.
- An arch test lists every ability passed to `can`, `authorize`, `Gate::allows` and the `can:` middleware, and fails
  when the matching policy has no method of that name.

## Status codes

- `Response::denyAsNotFound()` or `Response::denyWithStatus(404)` makes a denial answer 404 instead of 403. Use it
  where a denial would otherwise confirm existence. Inside the tenant, a member without the permission gets 403.
- Prefer resolving resources through the tenant (see `tenant-isolation`), so foreign records never reach the policy.

## Permissions in checks

- Ability names are catalog values: `Gate::allows(Permission::BookingsCancel->value)` or a policy method that
  checks the enum member. No string literals at check sites.
- The permission check calls the central effective-permissions service; policies do not compare `owner_id`
  themselves.

## Mass assignment

- `is_admin`, staff flags, `owner_id`, tenant foreign keys and role pivots stay out of `$fillable`. Set them in the
  services that own those changes.

## Tests

- Policy tests go through the real check (`$member->can(...)`, `Gate::forUser(...)`), not by calling policy methods
  directly, so the base `before()` runs.
- The matrix and escalation tests from `guard-artifacts.md` (same skill) cover the rest.
