# Architecture

Load when laying out an MCP server inside a product: layers, the request pipeline, connections and tokens, tenant
binding, the rights model, audit, transport and routing, performance, or the laravel/mcp package.

## Contents

- Layers
- Request pipeline
- Connections and tokens
- Tenant binding
- Rights model and tool visibility
- Audit and recent changes
- Transport, host and routing
- OAuth
- Performance and data-source failures
- Stack notes: laravel/mcp v1.1.2

## Layers

- The MCP server runs inside the product application as one more entry point, next to the UI controllers and the
  public API. It calls domain services directly. A separate service that calls the product's own HTTP API adds a
  network hop and a second auth model without adding a check.
- Keep a registry of tool classes with schema, required rights, effect class and handler. The same registry can
  later back an in-product assistant that runs under the signed-in user instead of a token.
- Presenters: one per exposed model, with an explicit field list. Never reuse API resources or a model's array
  form; they change when the API changes and they decrypt encrypted attributes.
- Before the first tool, move every protective check out of form requests and controllers into services. Where the
  UI wrote inline, create the service, then make UI and API use it too. Pin the field lists of each service against
  the request validators with a test.

## Request pipeline

Every `tools/call` passes the same steps. The tool's own handler is the only step a tool author writes, and the
base class makes the entry method final so no tool can skip the rest.

1. Reset per-request state left by a long-lived worker (current tenant, scoped singletons).
2. Kill switch: global flag on, return 503 with `Retry-After`.
3. Pre-auth rate limit per client address.
4. Bearer missing or invalid: 401 with `WWW-Authenticate: Bearer` and a short text that says how to connect.
5. Resolve the token: prefix, hash lookup, not revoked, not expired, type MCP.
6. Bind the connection: tenant exists, is not being deleted, has MCP enabled and a plan that allows it; creator
   exists and is an active member; live rights = token rights ∩ creator's current rights; bind the context; set the
   audit channel. No framework guard user.
7. Visibility: one function returns the reason a tool is unavailable for this context, or nothing.
8. Normalize and validate arguments (see `tool-design.md`); unknown fields are an error.
9. Limits: rate bucket for the effect class, concurrency slot, loop brake.
10. Replay check for silent writes.
11. Handler: read, prepare a preview, or execute through the service.
12. Translate: domain exceptions to tool errors, results to the shared shape in both channels.
13. Record usage counters (tool, outcome) after the response, at most once per minute per token for `last_used_at`.

## Connections and tokens

| Property | Choice |
|---|---|
| Format | Own prefix plus at least 256 bits from a CSPRNG; stored as SHA-256; shown once |
| Binding | Tenant and creating person, both not null for this token type (a check constraint) |
| Rights | Capped at the creator's rights on creation, intersected live on every call |
| Settings per connection | Toolset, approval mode (client or product UI), effect switches (notify customers, page people, change alerting, move money), client label |
| Expiry | A default such as 90 days with a few choices; "never" only for the tenant owner |
| Renewal | New token with the same settings, old one revoked at once |
| Revocation | Through a service that writes an audit entry, also when a member is removed |
| Usage | `last_used_at` and last client name; no client IP address |
| Cap | A small maximum number of connections per tenant |

Three independent locks keep MCP tokens out of the full API:

1. The API token resolver accepts only its own prefix.
2. The API auth middleware checks the token type itself, not only a later ability check.
3. Every token introspection used by other services filters by type.

## Tenant binding

- Default: one connection, one tenant. A consultant who serves several customer tenants adds one server entry per
  tenant in the client (`bookings-tenant-a`, `bookings-tenant-b`).
- A token for several tenants needs the tenant in the transport, for example a path segment, checked against the
  token's allowed tenants on every request. Never a tool argument: the model would pick it, the tool list could not
  match two plans, and switching the bound tenant per call in a long-lived worker leaks state.
- A tenant admin must be able to switch agent access off for that tenant without touching other tenants.
- Any foreign reference in arguments resolves inside the bound tenant. A foreign public ID behaves exactly like a
  missing one (see `tenant-isolation`).
- Actions that belong to a person (a comment, "my" draft, "my" absence) run as the connection's creator. Without a
  creator they are refused.

## Rights model and tool visibility

- Real permissions come from the product's permission catalog (see `authorization-rbac`).
- For the connection dialog, group permissions into areas with levels read, write and delete. A level sets all
  permissions of its area; the matrix still allows single permissions.
- Templates: read only (the default), read and write, full, custom. A template sets a level only where the creator
  holds it completely.
- Effect switches are independent of permissions. The template "read and write" may switch on the milder ones; the
  most dangerous switch stays an explicit choice.
- Plan features such as MCP read and MCP write: a missing key in a stored plan counts as false, so add a backfill
  migration when the feature appears.
- One function decides visibility and returns the reason, in this order: no connection, tool not in the
  connection's toolset, write tool on a read-only plan, plan feature missing, permission missing (live), effect
  switch off. `tools/list` lists a tool only when the reason is empty. `tools/call` on a hidden tool returns a tool
  error with the reason, because a client keeps showing a tool it listed before the change until it reloads.

## Audit and recent changes

- Audit rows get `channel` and `channel_context` columns, set at the three entry points (UI, API, MCP). Putting the
  channel into a free-form metadata field breaks exact metadata assertions across the suite.
- The tenant's activity page shows the channel and the client name and filters by them.
- `list_recent_changes` reads what this connection created or changed, with handles and states. If audit writes
  are queued, the list lags by a few seconds; say so in the tool description.
- Telemetry is counters per tool, outcome, client and model: guard hits, errors, replays, previews without
  confirmation. No argument logs.
- Adding enum cases that queued audit jobs serialize: restart queue workers together with the web deploy, or old
  workers fail to deserialize the new value.

## Transport, host and routing

- Streamable HTTP, stateless, POST only, one JSON response per request. The 2026-07-28 revision removed sessions and
  the GET stream; a server may answer each request with JSON or an SSE stream, and plain JSON keeps workers free.
- A dedicated host with the root path as endpoint keeps URLs short. Once published, the canonical URL does not
  change: OAuth binds tokens to it.
- The MCP route sits outside the session and CSRF middleware groups. A browser GET on the endpoint can show a help
  page; GET and DELETE from older clients get 405.
- No redirects on the POST endpoint; some clients drop the `Authorization` header on redirects.
- Do not answer OAuth discovery while only bearer tokens are offered; a client that finds discovery metadata may
  start an OAuth flow instead of sending the configured header.
- Set the locale for the MCP route explicitly, before validation runs.
- Legacy clients still send `initialize`. A server that wants them keeps that path and pins it with an end-to-end
  test: legacy `initialize`, `tools/list`, `tools/call`.

## OAuth

Needed for clients that accept only OAuth and for directory listings. When implemented, the 2026-07-28
authorization spec requires Protected Resource Metadata (RFC 9728) on the server, audience validation of every
token, 401 for invalid or expired tokens, and no token passthrough; Client ID Metadata Documents are the
recommended registration, Dynamic Client Registration is deprecated. At consent, the user picks the tenant, and
each tenant becomes its own connection.

## Performance and data-source failures

- The concurrency cap protects workers, not the rate limit: a hanging data source turns a modest call rate into
  many blocked worker seconds. Cap concurrent calls per token and reserve one slot per instance for writes.
- Deadlines per tool class: short for reads, longer for expensive reads, a statement timeout inside write
  transactions. Do not change process-wide time limits from a tool in a long-lived worker.
- Paginate lists (for example 25 per page, at most 50) and keep results small; Claude Code warns above 10,000
  tokens and saves text results over 50,000 characters to a file (https://code.claude.com/docs/en/mcp, verified
  2026-10-31).
- When a data source is down, return `source_unavailable` and cache nothing; an empty result cached as "no data" is
  a false answer that outlives the outage.
- Run the MCP endpoint in its own deployment from the same image once traffic matters, so agent load and the UI do
  not take workers from each other.

## Stack notes: laravel/mcp v1.1.2

Read at the tag on 2026-10-31 (https://github.com/laravel/mcp/tree/v1.1.2). Re-check after each upgrade and pin
each point with a test.

- `Primitive::name()` falls back to `Str::kebab(class_basename($this))`; `description()` falls back to
  `Str::headline(class_basename($this))`. Set name, title and description explicitly.
- `HasAnnotations::annotations()` reads `(new ReflectionClass($this))->getAttributes()`. PHP returns only the
  attributes declared on that class, so `#[IsReadOnly]` on a base class does not reach a subclass. Derive the
  annotation array in a method from the effect class.
- `Server::$defaultPaginationLength` is 15 and `$maxPaginationLength` is 50. Raise both above the tool count so
  `tools/list` fits on one page.
- Exception mapping in `InteractsWithResponses` makes validation and authorization exceptions readable and returns
  "An internal server error occurred." for the rest. Catch domain exceptions in the pipeline and return tool errors.
- An unknown tool name throws a JSON-RPC error `-32602`, which matches the spec's protocol-error case. A tool that
  exists but is hidden for this connection is a different case: answer it with a tool error and the reason.
- `Response::structured()` JSON-encodes the array into a text item and sets the same array as structured content,
  so both channels match.
- `shouldRegister()` is resolved through the container on each listing; memoize expensive checks in the scoped
  context, not in a static.
- Install the package under `require`, not only transitively through a dev dependency, or a `--no-dev` production
  build lacks it.
