# Parity and tokens

Load when wiring the API to the UI's write path, building a Terraform provider or SDK on it, or designing tokens
and scopes for API consumers. Token permission rules are owned by `authorization-rbac`; agent tools by
`mcp-server-design`.

## One write path

```text
UI controller  ─┐
API controller ─┼─> domain service (validation bounds, plan limits, audit, events) ─> database
MCP tool       ─┘
Terraform provider ─> public API
```

- Controllers and tools translate input and output only. A write in an API controller that bypasses the service is
  a review finding.
- Validation bounds (lengths, ranges, enum values) are constants shared by request validation, the spec and the
  database CHECK constraints. A test compares them.
- Plan limits and permission checks sit in the service, so every surface enforces them.

## Parity list

A file in the repository, one row per resource field or action:

| Resource.field or action | UI | API | Terraform | MCP | Note |
|---|---|---|---|---|---|
| booking.notes | yes | yes | yes | yes | |
| booking.cancel | yes | yes | n/a | yes, with confirmation | Terraform manages config, not actions |
| resource.secret | write | write-only | sensitive | not exposed | sentinel |

CI fails when a spec change touches a resource and the list does not change in the same diff. Gaps stay visible
instead of being rediscovered by customers.

## Terraform-friendly responses

- Every writable field comes back in the read response with the same type, casing and normalization; the server
  normalizes on write, not on read.
- Lists that are sets on the server are returned sorted by a stable key.
- Server-set defaults are returned, so the provider can mark them computed instead of showing a diff.
- Secrets: the response holds a fixed sentinel; sending the sentinel keeps the stored value; the provider keeps the
  value from state and marks the attribute sensitive.
- Import works by public ID.
- Acceptance test per resource: create, plan expecting no changes, update one field, plan again, import, destroy.

## Tokens for API consumers

- Prefix per credential class (`bk_live_`, `bk_test_`) plus a random part; optionally a checksum so clients and
  scanners can reject typos without a lookup.
- Store a hash; show the plaintext once; keep a public ID and a last-used timestamp for the UI.
- Scopes are read and write per resource family, picked at creation, capped by the creator's own rights.
- Each route declares one required scope; a test lists all public routes and fails on one without a scope.
- Tokens for agents and for REST are separate classes if the products treat them differently; the class decides
  which surface accepts them.
- Expiry, rotation with a grace window, and revocation that takes effect on the next request, including cached
  idempotent replays.
- Audit entries name the token's public ID as the actor channel.
