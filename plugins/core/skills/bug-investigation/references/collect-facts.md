# Collect the facts

Write the facts block before any theory. Copy values from the source; mark anything you could not check as
reported.

## Facts block

```text
Source: [tracker issue link, log query, user report]
Exception and frame: [type, message, top application frame as path:line]
Release: [version or commit of the event]       Environment: [production, staging, ...]
First seen: [time with zone]    Last seen: [time with zone]    Frequency: [events per hour or day]
Affected: [count of tenants] tenants, [count of users] users   (counts only, no names)
Request: [method, route pattern, not the full URL with tokens]
Breadcrumbs: [the last steps before the error]
Changes near first seen: [deploys, config changes, dependency updates, data migrations, with times]
```

## Deploy correlation

- Put first seen next to the deploy history. An error whose first event follows a deploy by minutes has that
  deploy's diff as the first suspect.
- Check config and feature-flag changes, dependency updates and scheduled data migrations too. They do not always
  appear as deploys.
- An error present before the deploy and more frequent after it points at load or data, not only at the diff.
- First seen on a quiet date with no change nearby: look at data (a new customer, an unusual record, a month or
  year boundary, a time-zone change).

## Sources by tool type

- Error tracker. Sentry-compatible trackers keep issue-level fields such as first seen, last seen, event count
  and affected users, and event-level release, environment, tags, request and breadcrumbs. Read one full event,
  not only the issue summary; the summary groups events that can differ.
- Logs. Search by the request or trace ID from the event. Note the time window you searched.
- Metrics and traces. Error rate and latency around first seen; whether one endpoint, worker or region is
  involved.
- A person's report. Ask for the exact steps, what they expected and what happened, the time, the account (as an
  ID, not personal details in the chat), browser or client and version, and a screenshot if the view matters.

## Handle the data with care

- Copy counts and identifiers of the issue, not customer records. Do not paste personal data from events into
  notes, commits or chat.
- Tokens, cookies and authorization headers in a captured request are secrets. Remove them before quoting.
- Reading production data beyond the tracker is approval-tier under `safe-actions`.
