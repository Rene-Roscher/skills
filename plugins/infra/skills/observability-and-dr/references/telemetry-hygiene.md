# Logs, error tracker and traces

## Logs

- Structured (JSON) with fixed keys: time in UTC, level, service, version, trace ID, request ID, tenant handle.
- Redact at the logger with an allowlist of fields for request logs. Denylist at minimum: `authorization`,
  `cookie`, `set-cookie`, `password`, `token`, `secret`, `api_key`, query parameters named like these, full
  request bodies.
- Personal data: log a stable pseudonymous user handle instead of an email; keep IP addresses only with a stated
  retention; check the retention against the privacy notice.
- Access logs of internal endpoints must not contain secrets, which is one more reason never to put them in URLs.
- Unit test: feed a request with `Authorization: Bearer test-token-123`, a `password` body field and
  `?token=abc`; assert none of the three values appears in the captured output.

## Error tracker (Sentry SDK names; other SDKs have equivalents)

| Setting | Value | Reason |
|---|---|---|
| `send_default_pii` | false | no user IPs, cookies or headers by default |
| `include_local_variables` | false, or a filter | defaults to true in the Python SDK; locals often hold tokens |
| `max_request_body_size` | `never` for auth, payment and webhook routes | bodies carry credentials and personal data |
| `before_send` | strip `authorization`, cookies, `token`-like keys in extras, breadcrumbs and frame vars | runs after scope data is applied |
| server-side scrubbing | on, with project-specific fields | second layer; the data was still sent |

Test: a test transport captures the event of a deliberate error raised inside a function that holds a fake token
in a local variable and in a header; the captured JSON contains neither.

## Traces

- Propagate `traceparent` and `tracestate` on outgoing HTTP calls and inside queued job payloads; start a child
  span when the job runs.
- Put the trace ID into every log line and into error-tracker events, so one ID links all three.
- Head sampling at a stated rate per service; keep all traces that end in an error if the backend supports
  tail decisions.
- Span attributes follow the same redaction rules as logs. URLs with tokens in the query are redacted before
  export.
