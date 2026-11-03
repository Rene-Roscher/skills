# HTTP details

Load when writing problem types, pagination, the idempotency store, rate-limit headers or deprecation headers.
Standards read 2026-11-03: RFC 9457, RFC 9745, RFC 8594, RFC 6585, draft-ietf-httpapi-idempotency-key-header-08,
draft-ietf-httpapi-ratelimit-headers-11. Drafts change; re-read the current version before changing behaviour.

## Contents

- Problem details
- Pagination
- Idempotency store
- Rate-limit headers
- Deprecation and sunset

## Problem details

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation",
  "title": "The request has invalid fields.",
  "status": 422,
  "detail": "2 fields are invalid.",
  "instance": "/v1/bookings",
  "errors": [
    { "pointer": "#/starts_at", "detail": "Must be before ends_at." },
    { "pointer": "#/resource_id", "detail": "No such resource." }
  ]
}
```

- `type` is a stable URI per problem class with a docs page; `about:blank` means "nothing beyond the status code".
- Keep a problem-type registry in code (enum or constants) and generate the docs list from it.
- `title` does not change between occurrences; `detail` explains this one. Localize neither, or both.
- A referenced ID that does not exist or belongs to another tenant gives the same validation detail.
- Add a request ID extension member or header so support can find the log line.

## Pagination

```http
GET /v1/bookings?limit=50&cursor=eyJjIjoi...&filter[status]=confirmed&sort=-created_at

200 OK
{ "data": [ ... ], "next_cursor": "eyJjIjoi...", "has_more": true }
```

- The cursor encodes the last row's sort values and the filter set; a cursor used with different filters is a
  400 problem.
- Sort by allowlisted columns plus the public ID as tiebreaker; add the matching composite index.
- Encoding is not encryption: no internal ID or hidden field in the cursor.
- Totals are a separate, optional, possibly approximate field or endpoint.

## Idempotency store

| Column | Purpose |
|---|---|
| token public ID + key | unique scope |
| fingerprint | hash of method, path and canonical body |
| state | `processing` or `done` |
| status, headers subset, body | stored response, encrypted at rest |
| expires_at | documented retention |

Flow: insert `processing` with insert-on-conflict. Conflict with `processing` gives 409; conflict with `done` and a
different fingerprint gives 422; `done` with the same fingerprint replays after the current scope check, marked
with a header such as `Idempotent-Replayed: true`. Store only 2xx and deterministic 4xx outcomes; on a 5xx or a
crash, delete the row so the client can retry. Run the middleware after authentication and rate limiting. Keep
state in the shared store, never in instance memory.

## Rate-limit headers

```http
RateLimit-Policy: "default";q=600;w=60
RateLimit: "default";r=12;t=31
```

- `r` is the remaining quota, `t` the seconds in the effective window (draft 11, §4.1).
- On 429 send `Retry-After`; per the draft it takes precedence over the window, and should not point earlier than
  its end.
- One named limiter per surface (public API, auth, exports), keyed by token after authentication; unauthenticated
  routes key by IP. Expose the same constants on any limits endpoint.

## Deprecation and sunset

```http
Deprecation: @1790812799
Sunset: Thu, 31 Dec 2026 23:59:59 GMT
Link: <https://api.example.com/changelog#v1-bookings-legacy>; rel="deprecation"
```

- `Deprecation` is a structured-field date (`@` plus Unix seconds, RFC 9745); `Sunset` is an HTTP-date (RFC 8594);
  the sunset is not earlier than the deprecation.
- Keep a deprecation registry (route, deprecated at, sunset at, replacement, notice URL) that drives the headers,
  the docs and the changelog.
- Count calls per token to deprecated routes; notify owners at fixed intervals before the sunset.
- After the sunset answer `410 Gone` with a problem type that names the replacement.
