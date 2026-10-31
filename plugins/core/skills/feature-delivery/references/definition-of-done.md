# Definition of done

## Contents

- How to fill it in
- Checklist: correctness and security, architecture, data and performance, integration, user experience, proof,
  operations
- Example answers

## How to fill it in

Copy the checklist into the pull request description or the completion report. Under every item, write one answer
line, indented by two spaces:

- `met: [evidence]`: a test name, a command and its result, a screenshot, a link. "Done" or "yes" is not evidence.
- `rejected: [reason]`: why the item does not apply to this feature, in one specific clause. "Not needed" is not a
  reason; "no new data stored, the export streams existing rows" is.
- Work that still has to happen is not an answer. Open a tracked issue with a priority and write
  `rejected: deferred to [issue link], priority [P1-P3]`.

The DoD check in `guard-artifacts.md` rejects unanswered items and "later" without a link.

Several items point to skills in the `saas` plugin. Load the named skill when the item applies; this list says
what must exist, the skill says how.

## Checklist

### Correctness and security

- Tenant isolation tested on every surface the feature touches: web, API, export, webhook, realtime channel, job
  (`tenant-isolation`).
- Authorization enforced on the server. Frontend checks are user experience only (`authorization-rbac`).
- No internal sequential ID leaves the server: URLs, API bodies, exports, events, logs shown to customers
  (`dual-key-identifiers`).
- Input validated in one place, with bounds that match the database constraints.
- Privilege flags (admin, owner, role) cannot be set through mass assignment.
- Plan limits fail with a clear error message, not a 500.
- Administrative actions write an audit entry.
- New personal data has a defined retention, deletion and export path (`gdpr-engineering`).

### Architecture

- The project's layering is respected; UI and API write through the same domain service.
- No second mechanism for a problem the codebase already solves (cache, queue, notification, settings).
- Configuration is read only through the configuration layer, not from the environment at call sites.
- Async work runs on a deliberately chosen queue.
- Long-lived workers hold no request state between requests.

### Data and performance

- An index exists for every new filter, sort and join column, and no new index duplicates the prefix of another.
- No N+1 queries in lists, API resources, broadcast payloads or exports.
- Query count per request measured, with a frozen clock, against the plan's budget.
- Bulk behaviour checked at the planned peak volume.

### Integration

- Consumers and webhook handlers are idempotent.
- The API endpoint has pagination, documented error codes and rate limits.
- An infrastructure-as-code resource exists if the product ships a provider.
- Realtime events are authorized per channel and carry no other tenant's data.

### User experience

- Empty, loading, error, partial, no-permission and limit-reached states exist.
- Destructive actions ask for confirmation, with text that names the consequence.
- Keyboard use, focus order, labels and contrast checked.
- Every locale the product ships is complete.
- Support or staff can see what the customer sees.

### Proof

- Feature tests for each flow; unit tests for calculation and decision logic.
- A browser test where the flow is critical to the UI.
- Formatter and full suite run; the results are in the report.
- Verified in a running system (`verify-before-done`).

### Operations

- Rollout order and rollback written down.
- A feature flag, default off, where the change is risky.
- Errors reach the error tracker with useful context; a metric or alert exists where a silent failure would hurt.
- Customer documentation and internal specs updated.

## Example answers

From a project tool that adds CSV export of tasks:

```text
- Tenant isolation tested on every surface the feature touches.
  met: tests/Export/TaskExportTenantProbeTest, 4 probes (web, API, download link, job) return 404 for a foreign project
- An infrastructure-as-code resource exists if the product ships a provider.
  rejected: export is a one-off download, no configurable resource
- Every locale the product ships is complete.
  rejected: deferred to https://tracker.example.com/issues/88, priority P2
```
