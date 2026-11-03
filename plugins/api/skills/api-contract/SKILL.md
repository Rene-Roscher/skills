---
name: api-contract
description: "Designs and reviews public REST APIs as a contract: OpenAPI with drift and breaking-change gates, versioning, public IDs only, RFC 9457 errors, cursor pagination, Idempotency-Key on POST, per-token rate limits, Deprecation and Sunset headers, scoped tokens, parity with UI, Terraform and MCP, an API changelog. Use when adding or changing an endpoint or API field. Not for MCP tools or GraphQL."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# API contract

This skill decides what a public REST API promises its consumers and how the build keeps that promise: the shape
of resources, errors, lists, retries, limits and change over time. Framework syntax stays with the vendor docs and
the references below. Identifier format belongs to `dual-key-identifiers`, token permissions to
`authorization-rbac`, the agent surface to `mcp-server-design`. The failure this prevents: a field rename or a
changed error shape that breaks scripts, Terraform plans and integrations without anyone noticing before
customers do.

## Applies when / does not apply

- Applies: a new or changed public endpoint, field, filter, error, status code, header or list; API tokens and
  scopes; rate limits on the public API; a deprecation; the OpenAPI document; a Terraform provider or SDK built on
  the API; a feature that ships in the UI and must reach the API.
- Does not apply: MCP tool design (`mcp-server-design`), GraphQL schemas, internal endpoints only the own frontend
  calls (unless they are also public), outgoing webhook payload signing (`egress-and-webhooks`).

## Rules

Most important first. Examples use a booking API: bookings, customers, resources.

- [invariant] The OpenAPI document is the contract and lives in the repository. CI fails when a route exists
  without a spec entry or the other way round, when a response in the test suite does not validate against the
  spec, and when a diff against the last released spec contains a breaking change without a new version. Why:
  hand-maintained docs drift, and a breaking change in a minor release breaks clients silently. Test: rename one
  response field in a serializer; the contract test and the breaking-change diff both go red. Source: oasdiff,
  "Command-line tool to compare and detect breaking changes in OpenAPI specs" (https://github.com/oasdiff/oasdiff);
  OpenAPI Specification (https://spec.openapis.org/oas/latest.html); both verified 2026-11-03.
- [invariant] Breaking changes are defined in writing and need a new major version: removing or renaming a field,
  endpoint or enum value, changing a type or format, making an optional input required, tightening validation,
  changing a status code or error `type`, changing default sort or page size. Adding optional inputs, response
  fields, endpoints and enum values is not breaking, and the docs tell clients to ignore unknown fields and handle
  unknown enum values. Why: without the list every reviewer decides differently. Test: the diff tool's rule set
  matches the list; a fixture spec pair for each item is classified correctly. Source: reproducible with the test
  above.
- [invariant] Resources expose public IDs only: `id` and every reference field are opaque strings, URLs and
  `Location` headers use them, and foreign, missing and malformed IDs give the same 404. Why: sequential IDs
  enumerate records and leak volume. Test: the response-scanning guard from `dual-key-identifiers` runs over the
  API suite. Source: OWASP API Security Top 10 2023, API1
  (https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization, verified 2026-11-03).
- [invariant] Every error is `application/problem+json` per RFC 9457 with `type`, `title`, `status`, `detail` and
  `instance` where useful; validation errors add one extension member listing field and message per error. The
  same shape covers 400, 401, 403, 404, 409, 422, 429 and 500, carries no stack trace or SQL, and `type` values are
  stable and documented. Why: clients branch on `type`, not on English text. Test: one test per status asserts the
  media type and members; a forced exception in production mode shows no trace. Source: RFC 9457, "This document
  obsoletes RFC 7807" and the member definitions (https://www.rfc-editor.org/rfc/rfc9457.html, verified
  2026-11-03).
- [invariant] Every list endpoint is paginated with a documented maximum page size, a stable order with a unique
  tiebreaker, and a `next` cursor or link; an unbounded list does not exist. Why: a list that grows with the
  customer becomes a timeout and a memory spike. Test: request with `limit` above the maximum and get the maximum;
  insert rows between pages and see no duplicates or gaps. Source: reproducible with the test above.
- [invariant] Create endpoints accept an `Idempotency-Key` header: the key is scoped to the token, the stored
  record holds a request fingerprint and the response, a reuse with a different payload gets 422, a retry while
  the first request runs gets 409, a replay returns the stored response, and the expiry is documented. Before a
  replay the token's current scopes are checked again. Why: clients that lost a response retry and create
  duplicates. Test: same key and body twice gives one booking and identical responses; same key and different
  body gives 422; revoke the scope and the replay is refused. Source: draft-ietf-httpapi-idempotency-key-header,
  an active Internet-Draft (version 08), not an RFC: 422 for a different payload, 409 while processing, 400 when a
  required key is missing (https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/, verified
  2026-11-03).
- [invariant] Rate limits are keyed by token after authentication, with separate named limiters per surface, and
  a limited request gets 429 with `Retry-After`. Why: a limiter that runs before authentication counts per IP, so
  every customer behind one NAT shares one bucket, and unnamed limiters share one counter across routes. Test:
  assert the middleware order the framework actually executes; two tokens from one IP have separate buckets.
  Source: RFC 6585 §4, 429 "MAY include a Retry-After header" (https://www.rfc-editor.org/rfc/rfc6585.html#section-4,
  verified 2026-11-03).
- [invariant] Tokens carry scopes chosen at creation, a prefix that names the credential class, are stored as a
  hash and shown once; each route checks one scope. Details and rotation are in `authorization-rbac`. Why: a
  recognisable prefix lets secret scanners find leaked tokens, and least privilege limits a leak. Test: a token
  without the scope gets 403 problem details; the database holds no plaintext token. Source: GitHub, "token
  prefixes are a clear way to make tokens identifiable"
  (https://github.blog/engineering/platform-security/behind-githubs-new-authentication-token-formats/, verified
  2026-11-03).
- [invariant] Deprecation is announced in the response: `Deprecation` with a structured date, `Sunset` with an
  HTTP-date not earlier than the deprecation, and a `Link` with `rel="deprecation"` to the notice; usage of
  deprecated endpoints is counted per token so their owners can be told. Why: consumers notice headers in logs and
  tooling, and owners need to be contacted before removal. Test: a deprecated route returns all three headers with
  the dates from the deprecation registry. Source: RFC 9745, "The timestamp given in the Sunset HTTP header field
  MUST NOT be earlier than the one given in the Deprecation header field"
  (https://www.rfc-editor.org/rfc/rfc9745.html); RFC 8594, Sunset "indicates that a URI is likely to become
  unresponsive at a specified point in the future" (https://www.rfc-editor.org/rfc/rfc8594.html); both verified
  2026-11-03.
- [invariant] One write path: API controllers call the same domain services as the UI, the Terraform provider and
  the MCP server; validation bounds come from shared constants that match database constraints. Every writable
  field is readable back in the same shape, and secrets are write-only with a fixed sentinel that means "keep".
  Why: two write paths drift, and a field Terraform can write but not read produces a permanent diff. Test: a
  parity test creates the same booking through the UI action and the API and compares stored state; a provider
  acceptance test applies, then plans, and expects no changes. Source: reproducible with the test above.
- [invariant] Features reach every surface or are listed as gaps: a change that adds a field or action to the UI
  states whether the API, the Terraform provider and the MCP server get it in the same release, and the gaps live
  in one list. Why: customers who automate find missing fields only when their script fails. Test: a CI check that
  each spec change touching a resource also updates the parity list. Source: reproducible with the test above.
- [invariant] Consumers have an API changelog: dated entries, breaking changes and deprecations marked, linked
  from the `Deprecation` notice. A spec diff with changes requires a changelog entry. Why: a spec diff tells
  machines what changed, not people why. Test: a CI check fails when the released spec changes without a new
  changelog entry. Source: reproducible with the test above.
- [default] The major version is in the path (`/v1/`), and only breaking changes create a new one. Trade-off: URLs
  change on a major version, in exchange for versions that are visible in logs, docs and caches. Deviate only with
  an ADR that names this trade-off. Proof: the router has no unversioned public route.
- [default] Cursor pagination with an opaque cursor built from non-sensitive sort columns, for example
  `(created_at, id)` with the public ID. Trade-off: no jump to page N and no exact total by default, in exchange for
  stable pages under inserts and constant cost. Deviate only with an ADR that names this trade-off. Proof: decode a
  cursor; it holds no internal key.
- [default] Filters and sorts are allowlisted per endpoint; unknown query or body parameters on writes give 400 or
  422 instead of being ignored. Trade-off: clients cannot send extra fields, in exchange for typos that fail loudly
  instead of silently doing nothing. Deviate only with an ADR that names this trade-off. Proof: `filter[stauts]`
  returns a problem with the unknown parameter named.
- [default] Send `RateLimit` and `RateLimit-Policy` per draft-ietf-httpapi-ratelimit-headers (version 11, an active
  Internet-Draft), for example `RateLimit: "default";r=50;t=30`. Trade-off: the draft may still change and some
  clients only read older `X-RateLimit-*` names, in exchange for following the format the IETF is standardizing.
  Deviate only with an ADR that names this trade-off. Source:
  https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/, verified 2026-11-03.
- [default] Timestamps are RFC 3339 strings in UTC with `Z`; money is an integer in minor units plus an ISO 4217
  currency code. Trade-off: clients convert for display, in exchange for no time zone or float rounding
  ambiguity. Deviate only with an ADR that names this trade-off. Source: RFC 3339
  (https://www.rfc-editor.org/rfc/rfc3339.html, verified 2026-11-03).

## Procedure

1. Gate: does a client outside the own frontend call this, or will it? If not, stop.
2. Write the spec change first: paths, schemas with public IDs as strings, problem types, examples.
3. Classify the change against the breaking list. Breaking means a new version or a deprecation plan.
4. Implement through the domain service the UI uses; add the parity test.
5. Lists: cursor, maximum page size, allowlisted filters and sorts.
6. Creates: Idempotency-Key handling with fingerprint, 409, 422, scope re-check on replay.
7. Errors: problem details for every status the endpoint can return.
8. Auth and limits: required scope, named limiter keyed by token after authentication.
9. Deprecations: registry entry, headers, usage counter, owner notice.
10. Update the parity list for Terraform and MCP, and add the changelog entry.
11. Run contract tests, the breaking-change diff and the ID guard before review.

## Traps

- A framework's rate-limit middleware moved ahead of authentication by a priority list, so a limit documented per
  token was enforced per IP. Test the executed order, not the declared one.
- An error handler that returns problem details for API routes but HTML for unmatched routes or for exceptions
  thrown in middleware.
- An idempotent replay served from a store before the scope check, so a revoked scope still gets the old response.
- A response field added with `null` for old records breaks clients that typed it as required; document nullability.
- A generated spec that differs per environment because optional packages register routes only in development.
- A Terraform provider that reads a field the API returns in a different format (time zone, casing, ordering of a
  list) shows a diff on every plan.
- A paginated endpoint whose order changes with a new index, which a client sees as duplicates and gaps.

## Done when

- The spec is committed, contract tests validate every response in the suite, and the breaking-change diff runs in
  CI.
- Errors are problem details on every status; lists have a maximum page size and stable order.
- Creates honour `Idempotency-Key` with 409 and 422 and a scope re-check on replay.
- Rate limits are per token after authentication with 429 and `Retry-After`.
- Deprecated routes send `Deprecation`, `Sunset` and `Link`, and usage is counted per token.
- The parity list and the API changelog are updated in the same change.

## References

- [references/http-details.md](references/http-details.md): load when writing problem types, pagination, the
  idempotency store, rate-limit headers or deprecation headers.
- [references/parity-and-tokens.md](references/parity-and-tokens.md): load when wiring the API to the UI's write
  path, building a Terraform provider or SDK on it, or designing tokens and scopes for API consumers.

## Sources

- https://spec.openapis.org/oas/latest.html: OpenAPI Specification, version 3.2.1 at the time of reading, verified
  2026-11-03.
- https://github.com/oasdiff/oasdiff: breaking-change detection for OpenAPI, verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc9457.html: problem details, obsoletes RFC 7807, verified 2026-11-03.
- https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/: active Internet-Draft, version 08,
  verified 2026-11-03.
- https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/: active Internet-Draft, version 11,
  verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc6585.html#section-4: 429 and `Retry-After`, verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc9745.html: `Deprecation` header, Standards Track, March 2025, verified
  2026-11-03.
- https://www.rfc-editor.org/rfc/rfc8594.html: `Sunset` header, Informational, verified 2026-11-03.
- https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization: unpredictable IDs and
  object-level checks, verified 2026-11-03.
- https://github.blog/engineering/platform-security/behind-githubs-new-authentication-token-formats/: token
  prefixes for identification and secret scanning, verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc3339.html: timestamp format, verified 2026-11-03.
