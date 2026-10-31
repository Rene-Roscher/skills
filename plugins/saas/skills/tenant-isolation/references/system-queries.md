# System queries under automatic filters

Load when writing code that runs with no viewer while a global scope, RLS policy or visibility set is active:
scheduled tasks, notification fan-out, cascades, cleanups, billing counts, health checks of tenant resources.

## The question to ask

For each query on a filtered table: does this question have a viewer?

- Viewer questions ("which projects can this member see") keep the filter.
- System questions ("which members must be notified", "does this project still have tasks before we delete it",
  "which resources does the scheduler check", "how many seats is the tenant billed for") use the named opt-out,
  still scoped to the tenant.

## Patterns

- Named opt-out. One method or flag per filter, with a name that greps well (for example `withoutVisibilityFilter()`).
  Every call site has a comment with the reason and is listed in the guard allowlist.
- Generic removal counts too. Framework calls that drop all scopes or one scope by class name are escape hatches as
  well. The guard matches them, not only the named opt-out, so a generic removal cannot slip in unseen.
- Removal loops stay scoped. A "delete what the user did not submit" loop compares against the user's visible set
  only; otherwise it deletes records the user never saw.
- Aggregate first, filter after. Rollups and counts for billing or capacity are computed over the whole tenant and
  then shown per viewer.
- Cascades check unfiltered children. "Does this project still have tasks" runs without the visibility filter; with
  it, a cascade deletes children the actor could not see.
- Delivery-time checks. A notification job re-reads recipients through the recipient choke point when it runs.

## Tests

- A test trait binds a restricted viewer (a member who sees one project of three) before the system code runs.
- Each system path runs once unbound and once with the restricted viewer bound; the results are equal.
- The structural guard pins the count of opt-outs and generic removals. A new one fails the build until it is added
  to the allowlist with a reason, so every exception is a reviewed change.

## Smells

- A scheduler or listener class that reads the current user or current tenant from ambient state.
- A count that differs between an admin's and a restricted member's session.
- A cascade or cleanup that passes in tests only because fixtures never bind a restricted viewer.
