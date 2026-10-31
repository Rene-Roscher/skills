# Jobs, caches, exports, recipients and channels

Load when writing background work or any path where tenant data leaves the request: caches, exports and downloads,
notifications and webhooks, realtime channels, analytics and search stores.

## Jobs and scheduled tasks

- Constructor takes scalars: tenant ID, resource IDs, actor ID if the job acts for someone. No models whose loaded
  relations go stale, no ambient tenant.
- `handle()` resolves each resource through the tenant and stops when the tenant is gone, pending deletion or
  suspended, the member is deactivated, or the resource was deleted. It records why it skipped.
- Tenant-dependent values (tax treatment, locale, plan limits, time zone) are passed in or resolved from the tenant
  inside the job. Never read them from config or context that a request set.
- Fan-out jobs dispatch one job per tenant and pass the tenant ID. A single job that loops over tenants binds
  nothing globally while it loops.
- Framework context propagation (for example Laravel Context, which is dehydrated into the job payload and hydrated
  when the job runs, https://laravel.com/docs/12.x/context, verified 2026-10-31) is fine for log and trace fields.
  It is not an input for data selection or authorization.

## Caches

- Key or tag includes the tenant: `workspace:{id}:dashboard`.
- If the value depends on what the viewer can see, the key includes a viewer fragment: a short hash of the sorted
  visible project IDs or of the viewer's role set. Two viewers with the same visible set share the entry.
- Invalidate through the keyspace you wrote: entries stored under tags are removed by flushing the tag. A bare key
  delete does not touch a tagged entry. Laravel's docs say tagged items "may not be accessed without also providing
  the tags that were used to store the value", and tags are unsupported on the `file`, `dynamodb` and `database`
  drivers (https://laravel.com/docs/12.x/cache, verified 2026-10-31).
- Every write that changes a cached value invalidates it in the same transaction's after-commit hook.
- A TTL bounds staleness. It does not replace invalidation.

## Exports and downloads

- Generation selects through the tenant and the requesting actor's visibility at the time of the request.
- The file path is random and the download endpoint still checks membership and the export permission when the
  file is fetched. A signed URL with a short expiry may replace the second check only if the ADR says so.
- Buckets behind a CDN grant no list action to public principals. Check the policy in infrastructure CI.
- Files expire. A retention job deletes them; its schedule is part of the privacy record (see `gdpr-engineering`).

## Notifications, mails, webhooks, SMS

- One recipient service applies tenant, active membership and preferences. Every channel calls it, at send time.
- Payloads carry only the tenant's own data and public IDs.
- Webhook endpoints are tenant configuration: create, update, test-send and delivery logs are probed like any other
  tenant resource.

## Realtime channels

- Channel names use public IDs: `workspace.{publicId}`, `project.{publicId}`.
- The authorization callback checks the tenant, active membership, the permission and the visible set.
- Tests call the registered callbacks directly. In Laravel 12.x, the `null` broadcaster's `auth()` has an empty
  body, so a test that goes through the HTTP auth endpoint with that driver never runs the callback
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Broadcasting/Broadcasters/NullBroadcaster.php,
  verified 2026-10-31).
- Deactivation ends channel authorization; a reconnect after deactivation fails.

## Secondary stores

- Analytics, search and object storage get IDs only after a tenant-scoped lookup in the primary store.
- Every query function on them takes the tenant as a required parameter, and the query filters on it.
- Search indexes store the tenant ID on every document and filter on it in every query.
