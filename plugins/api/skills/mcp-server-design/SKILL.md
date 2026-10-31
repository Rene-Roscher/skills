---
name: mcp-server-design
description: "Designs and reviews MCP servers that agents use safely on multi-tenant products: tools as an adapter on the service layer, one tenant per connection bound in the token, rights checked per call, effect classes with preview and confirmation, replay protection, kill switch, error shapes, model evals. Use when building or reviewing MCP tools or servers. Not for using MCP servers or REST design."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# MCP server design

This skill decides how an MCP server exposes a product to agents: where tools sit in the code, how a connection
binds to one tenant and one person, which calls need a person's confirmation, and how results and errors lead the
model to the next correct call. Protocol syntax stays with the MCP specification (revision 2026-07-28 when this
was written) and the SDK docs. Query scoping, permission catalogs and ID formats come from `tenant-isolation`,
`authorization-rbac` and `dual-key-identifiers`. The failure this prevents: a model that picks the wrong tenant,
mails a customer twice or acts on text a third party planted, because the server left a gate to the model, the
client or a tool description.

## Applies when / does not apply

- Applies: building an MCP server for a product, adding or reviewing a tool, choosing how MCP credentials bind to
  tenants and people, tools that notify customers, page people, mute alerts or delete, duplicate writes after
  client retries, error and result shapes, tool names and descriptions, toolsets for small models, evals of tool
  use.
- Does not apply: configuring a client to use someone else's MCP server, REST or GraphQL endpoint design, chat
  bots and slash commands that are not MCP, prompt writing for a product's own assistant, rate limits on
  non-MCP routes.

## Rules

Most important first. Examples use a booking system: bookings, customers, technicians.

- [invariant] The server enforces what must not go wrong; descriptions and annotations only steer. Every gate below
  runs in server code on every call. Why: annotations are hints, and clients exist that auto-approve or never
  prompt. Test: call each guarded tool from a raw JSON-RPC client that ignores hints; every guard still fires.
  Source: MCP schema 2026-07-28, `ToolAnnotations`: "Clients should never make tool use decisions based on
  `ToolAnnotations` received from untrusted servers" (https://modelcontextprotocol.io/specification/2026-07-28/schema,
  verified 2026-10-31).
- [invariant] Tools are a second adapter on the service layer: they call the same domain services as the UI and the
  API, never the own HTTP API in a loopback and never the ORM directly. Checks that protect data (limits, URL
  allowlists against SSRF, ownership of referenced records) live in the service, not only in a controller or form
  request. One write path per function. Why: a thin adapter inherits every check that only its sibling adapters
  ran. Test: an arch test fails on persistence calls in tool classes; per write tool, an input the API rejects is
  rejected by the tool. Source: reproducible with the test above.
- [invariant] One connection, one tenant: the tenant is bound in the credential when the connection is created,
  no tool schema has a tenant parameter, an argument like `workspace_id` is rejected as unknown, and every handle
  is resolved inside the bound tenant. A credential that serves several tenants carries the tenant in the transport
  (path or header) and checks it against the credential, never in a tool argument. Why: a tenant parameter lets the
  model choose the tenant. Test: per tool with a reference, pass another tenant's valid handle; expect `not_found`
  and an unchanged row. Source: MCP tools spec, the tool set "MAY vary by the authorization presented on the
  request" (https://modelcontextprotocol.io/specification/2026-07-28/server/tools); security best practices, key
  state by a user ID "derived from the verified token rather than supplied by the client"
  (https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices); both verified
  2026-10-31.
- [invariant] Rights are cut live: effective rights = token rights ∩ current rights of the person who created the
  connection, computed on every `tools/list` and `tools/call`. Token rights are capped at creation, a removed or
  deactivated creator ends the connection, revocation runs through a service that audits. Why: rights frozen into a
  token outlive a role change. Test: remove the creator's role, call a write tool; refused on the next call. Source:
  MCP tools spec, servers MUST "Implement proper access controls" (verified 2026-10-31).
- [invariant] No ambient user on MCP requests: middleware binds a connection context (tenant, creator, live rights)
  and leaves the framework's current-user slot empty; tools read the actor from the context, services take the actor
  as a parameter. Why: with the owner set as current user, a stray policy check in a tool passes because owners may
  do everything; with no user it fails closed. Test: an arch test bans gate, policy and current-user helpers in tool
  code; a deliberately added policy check makes the call fail. Source: reproducible with the test above.
- [invariant] Each tool has exactly one effect class: read, silent write, notify (reaches customers or changes what
  they see), wake (pages or calls a person), alerting (mutes, pauses or reroutes alerts), delete. Derive the class
  from the code path (events, listeners, observers, jobs, mails), not the name, and split a tool that spans two.
  Why: hints, rate bucket, preview duty and connection switch follow from the class. Test: with queue, mail and
  event fakes, silent tools dispatch no notification. Source: connector review criteria, catch-all read/write tools
  are rejected and writes are split by action type (https://claude.com/docs/connectors/building/review-criteria,
  verified 2026-10-31).
- [invariant] Notify, wake, alerting and delete take two steps. The tool only prepares: it stores a pending action
  (connection, tool, normalized arguments and digest, hash of the content that will go out, expiry) and returns
  `PREVIEW`, a `confirm_token` and a server-written `confirm_summary`. Only `confirm_action` executes, after checking
  connection, unused, unexpired, not rejected, exact summary, a lock, live rights and switches, and a fresh
  preparation whose content hash still matches (else a new preview, old token dead). Why: neither model nor client
  reliably asks a person, and approved text can change in between. Test: preview alone sends nothing; reused,
  expired, foreign and wrong-summary tokens fail; an edit between steps yields `changed_since_preview`. Source: MCP
  tools spec, "there SHOULD always be a human in the loop with the ability to deny tool invocations"; MRTR server
  requirements: state echoed by a client is "attacker-controlled input", bound to principal, short expiry and
  parameter digest, single use enforced server-side
  (https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr); both verified 2026-10-31.
- [invariant] Replay protection on every silent write: fingerprint = connection + tool + SHA-256 of the canonical
  JSON of the normalized arguments (keys sorted at every level); a hit inside the window returns the first result
  with `replayed: true` and runs nothing. An optional `idempotency_key` is bound to the argument digest. The cache
  holds presenter output, never one-time secrets. Why: a broken stream loses the in-flight request and clients MUST
  re-issue it with a new ID, so a write that ran arrives again. Test: same call twice with different JSON-RPC IDs;
  one row, second result `replayed: true`. Source: MCP changelog 2026-07-28, major change 9
  (https://modelcontextprotocol.io/specification/2026-07-28/changelog); Claude Code repeats a pending call to tools
  marked `idempotentHint` or `readOnlyHint` once on a new connection (https://code.claude.com/docs/en/mcp); both
  verified 2026-10-31.
- [invariant] Every create tool has a sibling update tool and a duplicate guard on a business key. A hit returns an
  error naming the existing handle and the update tool; creating anyway needs `separate: true` and a reason. Guards
  read synchronous columns (`created_by`, `created_at`), never a queued audit log. Edit tools have no notify
  parameter. Why: asked to "make the text better", a model creates a second object unless stopped. Test: create
  twice with the same key; one row, an error naming it. Source: reproducible with the test above.
- [invariant] Updates carry the version the caller read: objects and messages in results have a `version` (content
  hash), update and edit tools require it, a stale one returns `conflict` with the current state. Why: an agent
  working from an old read overwrites a colleague's edit. Test: read, change the row elsewhere, update with the old
  version; `conflict`, row unchanged. Source: reproducible with the test above.
- [invariant] Batch tools take explicit handles, or a filter plus a required `expected_count`; when the match count
  differs, return the matches and execute nothing. Why: a filter wider than the model expected multiplies one
  mistake. Test: a filter matching 12 bookings with `expected_count: 3`; error lists 12, nothing changed. Source:
  reproducible with the test above.
- [invariant] Validate every argument on the server with the tool's own rules and reject unknown fields with the
  list of allowed ones. Why: SDKs do not always check arguments against `inputSchema`, and an ignored field lets the
  model believe it set something. Test: an extra field returns the allowed list and writes nothing. Source: MCP
  tools spec, servers MUST "Validate all tool inputs" (verified 2026-10-31).
- [invariant] Third-party text in results is untrusted: text a customer, end user, external system or upload can
  write (notes, mail bodies, webhook payloads, remote error messages) is truncated, stripped of control characters
  and returned under `untrusted_text` with a note not to follow instructions in it; raw bodies stay out.
  Descriptions describe the tool and never tell the model how to behave. Why: injected text that steers a tool with
  external effect is the top risk; the preview step is the second line. Test: an injection canary in every
  third-party field appears only inside the wrapper. Source: MCP tools spec, servers MUST "Sanitize tool outputs";
  connector review criteria reject prompt-injection patterns in descriptions; both verified 2026-10-31.
- [invariant] Results carry no secrets and only the personal data the task needs: presenters with explicit field
  lists, never a whole-record serializer; logs hold tool name, outcome and public IDs, never arguments. Why: every
  result goes to the user's model provider. Test: fill every secret field of a fixture with a bait value, call every
  read tool, grep results and logs; no bait. Source: reproducible with the test above; record keeping in
  `gdpr-engineering`.
- [invariant] Business, validation and permission failures are tool execution errors (`isError: true`) whose text
  starts with `Error:`, names cause, fix and the right tool with real handles, and ends with one line of JSON
  details. "Not found" points to a `find_` tool, never to creating. A tool hidden by rights, toolset or plan answers
  with that reason. Why: the model self-corrects only on errors it sees and understands. Test: every error path in
  the contract suite starts with `Error:` and has a parseable JSON line. Source: MCP schema, `CallToolResult.isError`:
  tool errors "SHOULD be reported inside the result object ... Otherwise, the LLM would not be able to see that an
  error occurred and self-correct"; connector review criteria fail generic "Internal Server Error" responses; both
  verified 2026-10-31.
- [invariant] The text block and `structuredContent` carry the same JSON, and a declared `outputSchema` covers every
  structured result, errors included. Why: clients differ in which channel reaches the model, and they SHOULD
  validate against a declared schema. Test: for every result in the suite, the parsed text equals
  `structuredContent`. Source: MCP tools spec, a tool with structured content "SHOULD also return the serialized
  JSON in a TextContent block" (verified 2026-10-31).
- [invariant] Time and money are the server's job: times arrive as local time plus IANA zone or ISO 8601 with
  offset, never without; nonexistent and ambiguous local times are rejected with the options; every time in a
  result shows weekday, local time with zone, UTC and distance from now. Totals, tax and rounding are computed on
  the server from decimal strings or integer minor units. Why: off-by-one-day and DST errors are invisible without
  the weekday. Test: `2026-03-29 02:30` in `Europe/Berlin` is rejected; `2026-10-25 02:30` returns both offsets.
  Source: reproducible with the test above.
- [invariant] A kill switch in one place: a global flag, set by a CLI command and an admin toggle that both audit,
  makes every MCP call return 503 with `Retry-After` while connections stay; a per-tenant switch with its default
  defined once lets a tenant admin turn agent access off. Why: an incident needs one move that stops all agent
  writes. Test: flag on, call a write tool; 503, no row, no job. Source: reproducible with the test above.
- [invariant] Every MCP write is audited with channel `mcp`, connection and client name, set at the entry point as
  columns, and `list_recent_changes` shows what this connection changed. Why: tenants see what an agent did, and an
  agent that lost context finds its draft instead of creating another. Test: each write tool yields exactly one
  audit row with channel `mcp`. Source: reproducible with the test above.
- [invariant] MCP and API credentials do not cross: MCP tokens have their own type and prefix, are stored hashed,
  shown once, and are rejected by every API route; API tokens and session cookies are rejected by the MCP endpoint.
  With OAuth, accept only tokens issued for this server and never pass one through. Validate `Origin`. Why: MCP
  tokens sit in plain text in client config files. Test: each pairing returns 401; a bad `Origin` returns 403.
  Source: MCP authorization spec, servers "MUST NOT accept or transit any other tokens"
  (https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization); Streamable HTTP, servers MUST
  validate `Origin`; both verified 2026-10-31.
- [invariant] Launch gate: contract tests per tool, arch tests and a manifest snapshot run in CI, and evals with
  real models on a held-out set show zero duplicates in revision scenarios, zero unwanted external effects, zero
  execution without confirmation, zero cross-tenant access and zero generic errors before write tools ship. Every
  description change passes the same gate. Why: tests prove the server; only model runs prove models use it right.
  Test: the eval report of the release candidate. Source: "We relied on held-out test sets to ensure we did not
  overfit" (https://www.anthropic.com/engineering/writing-tools-for-agents, verified 2026-10-31).
- [default] Approval happens in the client for clients that prompt per call, and through an approval link in the
  product UI for clients that do not; steps that move money or are legally binding always use the product UI, and
  only someone holding the right for the action may approve. Trade-off: one more click and a page to build, in
  exchange for a guaranteed person. Deviate only with an ADR that names this trade-off. Source: Claude Code's
  `_meta["anthropic/requiresUserInteraction"]` forces a prompt per call and in a mode that never prompts "Claude
  Code denies the call instead" (https://code.claude.com/docs/en/mcp, verified 2026-10-31).
- [default] Typed handles: kind prefix plus public ID (`bkg_` plus a NanoID) in every result; accept the handle, the
  bare public ID or a console link; a wrong kind gets an error naming both kinds; internal IDs never appear (see
  `dual-key-identifiers`). Trade-off: a parsing step, in exchange for precise errors when a model mixes up IDs.
  Deviate only with an ADR that names this trade-off. Source: MCP tools spec, stateful tools: "a handle is a name,
  not a capability" (verified 2026-10-31).
- [default] Names and descriptions: snake_case `verb_object` up to 40 characters; `find_` searches, `list_` returns
  short full lists, `get_` returns one object; the effect is in the name (`send_booking_confirmation`), never in a
  parameter; every tool has a `title` and an explicit `readOnlyHint` or `destructiveHint`. Descriptions are English
  and lead with what and when in at most 300 characters, then what the tool does not do and its sibling, the effect,
  parameters and one JSON example. Server instructions stay under 4,096 characters, and every critical rule in them
  also appears in the descriptions and results. Trade-off: longer descriptions cost context. Deviate only with an ADR that names
  this trade-off. Source: connector review criteria (names up to 64 characters, title and hints); Claude Code cuts
  instructions and upfront descriptions at 4,096 characters; both verified 2026-10-31.
- [default] Results lead on: `summary` (resulting state and who was notified), objects with handle, `version`,
  state and link, `notified` on every write, `warnings`, and `next_steps` as exact calls with real handles, each one
  tested verbatim. Trade-off: larger results; Claude Code warns above 10,000 tokens. Deviate only with an ADR that
  names this trade-off. Source: "return only high signal information back to agents" (Anthropic, writing tools for
  agents); Claude Code output limits (https://code.claude.com/docs/en/mcp); both verified 2026-10-31.
- [default] Tolerant input, strict meaning: coerce `"true"`, `"5"`, arrays sent as JSON strings, enum synonyms and an
  exact name with one match, and report each coercion in `warnings`; several matches return up to five candidates;
  writes never fuzzy-match. Trade-off: a normalization layer, in exchange for small models that succeed instead of
  looping. Deviate only with an ADR that names this trade-off. Proof: one contract test per coercion.
- [default] Toolsets bound to the connection: a core set of about 20 tools with short descriptions for small and
  local models, a standard set, a full set; `tools/list` returns all permitted tools on one page in a fixed order;
  no search wrapper that hides per-tool annotations. Trade-off: several catalogs to test. Deviate only with an ADR
  that names this trade-off. Source: MCP tools spec, servers "SHOULD return tools in a deterministic order"
  (verified 2026-10-31).
- [default] Limits per effect class: rate buckets per token and tenant for reads, expensive reads and writes;
  notify limited per object, wake per tenant; two concurrent calls per token with a worker slot reserved for writes;
  a deadline per tool; a loop brake that answers the third identical failing call with "stop and ask the user".
  Trade-off: a legitimate burst waits. Deviate only with an ADR that names this trade-off; limits themselves are not
  optional. Source: MCP tools spec, servers MUST "Rate limit tool invocations" (verified 2026-10-31).

## Procedure

1. Gate: does the server act on tenant data for a person? If it only serves public read-only data, apply the rules
   on names, results, errors, untrusted text and limits, and stop.
2. Harden the service layer first: validation inside services, field allowlists instead of mass assignment, no
   secrets in serializers. Read the event and job wiring of every service a tool will call.
3. Inventory write functions from the routes; mark each "via MCP" or "not, because ..." (secrets, member and role
   management, billing, uploads and token creation usually stay out).
4. Build the pipeline once: auth, kill switch, context binding, visibility, normalization and validation, limits,
   replay, handler, result and error translation, audit. Tools cannot bypass it.
5. Ship in order: read tools with result and error shapes plus the eval harness; silent writes with guards, replay
   and versions; preview tools with `confirm_action`; configuration last.
6. Per tool: effect class from the code path, name, flat schema, description, guard key, presenter, contract tests.
7. Dump `tools/list` and run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_tool_manifest.py tools.json`.
8. Run evals on the held-out set, then a live session with two clients, one that reads `structuredContent` and one
   that reads only text.

## Traps

- SDK defaults name a tool after its class. In laravel/mcp v1.1.2 the name is the kebab-cased class name and the
  description is the class name as a headline. Set both explicitly and pin them with an arch test.
- Hints set as class attributes on a base class may not reach subclasses: laravel/mcp v1.1.2 reads annotations from
  the concrete class with `getAttributes()`. Derive hints in one method from the effect class.
- laravel/mcp v1.1.2 paginates `tools/list` at 15 by default and turns every exception except validation and
  authorization into "An internal server error occurred." Raise the page size and translate domain exceptions.
- A preview served from the replay cache shows the old text. Previews are always prepared fresh.
- A duplicate guard that reads a queued audit log is green with a sync test queue and too late in production.
- A "do not notify" flag on create can mean "disarm the later publish". Read what the flag does in the service.
- "Group related operations into one tool with an action parameter" fits reads with the same hints. On writes it
  puts two effect classes behind one approval, and the connector directory rejects mixed read/write tools.
- A `next_steps` entry that the suggested tool cannot execute sends the model into a loop.
- Error texts in the app's default locale leak into English tool output unless the MCP route sets its locale.

## Done when

- `check_tool_manifest.py` passes on the current `tools/list` dump, and the manifest snapshot is committed.
- Per tool with a reference: a foreign handle returns `not_found` and writes nothing.
- Per effect class above silent write: preview alone does nothing; confirmation executes exactly once.
- Replay, duplicate, version, batch-count and unknown-field tests are green for every write tool.
- Canary tests for secrets and injection are green over all read tools.
- Kill switch, credential separation and live-rights tests are green.
- The eval gate holds on the held-out set for each model the release targets.

## References

- [references/architecture.md](references/architecture.md): load when laying out the server, the connection and
  token model, tenant binding, the rights model, audit, transport and routing, or when using laravel/mcp.
- [references/tool-design.md](references/tool-design.md): load when writing or reviewing a single tool: effect
  class, name, schema, description, result and error shape, input normalization, time and money, guard keys,
  toolsets.
- [references/safety.md](references/safety.md): load before the first write tool: preview and confirmation,
  approval modes, replay protection, limits, loop brake, kill switch, threat model, privacy.
- [references/testing.md](references/testing.md): load when writing contract and arch tests or building the eval
  harness and launch gate.
- `${CLAUDE_SKILL_DIR}/scripts/check_tool_manifest.py`: run over a `tools/list` JSON dump. `--help` lists options;
  `--self-test` proves it catches each defect class.

## Sources

- https://modelcontextprotocol.io/specification/2026-07-28/server/tools: tool list per authorization, deterministic
  order, structured content mirrored in text, output schema, error kinds, security considerations, stateful
  handles, verified 2026-10-31.
- https://modelcontextprotocol.io/specification/2026-07-28/schema: `ToolAnnotations` are hints with defaults
  `readOnlyHint` false, `destructiveHint` true, `idempotentHint` false, `openWorldHint` true; `isError` semantics;
  latest protocol version 2026-07-28, verified 2026-10-31.
- https://modelcontextprotocol.io/specification/2026-07-28/changelog: stateless protocol, no sessions, broken
  streams re-issued by clients, verified 2026-10-31.
- https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr: echoed state is attacker-controlled,
  integrity, principal, expiry, digest, single use, verified 2026-10-31.
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization: authorization optional, protected
  resource metadata, audience validation, no token passthrough, verified 2026-10-31.
- https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http: `Origin` validation,
  JSON or SSE per request, verified 2026-10-31.
- https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices: state handles bound
  to the verified principal, token passthrough, scope minimization, verified 2026-10-31.
- https://claude.com/docs/connectors/building/review-criteria: split read and write tools, title and hints, names
  up to 64 characters, actionable errors, prompt-injection patterns, verified 2026-10-31.
- https://code.claude.com/docs/en/mcp: description and instruction cut-offs, output limits, repeat of idempotent
  calls, `anthropic/requiresUserInteraction`, verified 2026-10-31.
- https://www.anthropic.com/engineering/writing-tools-for-agents: high-signal results, actionable errors, realistic
  evals, held-out sets, verified 2026-10-31.
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools: descriptions are "by far the most
  important factor in tool performance", verified 2026-10-31.
- https://github.com/laravel/mcp/tree/v1.1.2: default names, attribute-based annotations, page size 15, exception
  mapping, `Response::structured()` fills both channels, verified 2026-10-31.
