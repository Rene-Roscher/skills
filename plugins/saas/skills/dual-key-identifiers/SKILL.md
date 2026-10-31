---
name: dual-key-identifiers
description: "Designs and audits record IDs in multi-tenant SaaS: a bigint key for joins plus an opaque public ID (NanoID by default) for everything clients see, one 404 for foreign and missing IDs, a build check against leaks. Use when adding a table, model, route, serializer, export or webhook, choosing UUID, ULID or NanoID, or asked about auto-increment IDs or IDOR. Not for access rules (authorization-rbac)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Dual-key identifiers

This skill decides how records are identified inside the system and outside it. Every client-visible record gets
two keys: a bigint for joins and foreign keys, and an opaque public ID that is the only identifier a client ever
sees. The default public ID is a NanoID. Access control stays with `tenant-isolation` and `authorization-rbac`; an
unguessable ID never replaces it. The failure this prevents: sequential IDs in URLs, payloads or cursors that let
anyone enumerate records and read business volume.

## Applies when / does not apply

- Applies: a new table or model that clients will reference, a migration that adds or changes an ID column, a
  serializer or API resource, a route with a record parameter, cursor pagination, an export, an outbound webhook,
  a mail or realtime payload, a choice between UUID, ULID and NanoID, a pentest finding about IDOR or enumeration.
- Does not apply: who may act on a record (`authorization-rbac`), filtering queries to a tenant
  (`tenant-isolation`), primary-key or join tuning for tables no client sees, credentials and reset tokens, gap-free
  invoice numbers (`billing-eu-b2b`), content slugs that are public by design.

## Rules

Most important first. Examples use an invoicing app: invoices, customers, payments.

- [invariant] Internal sequential IDs never leave the trust boundary: keep identity, serial and auto-increment
  values out of URLs and route keys, JSON bodies, server-rendered page props and data attributes, pagination
  cursors, `Location` headers, exports, mails, outbound webhooks, realtime channel names and payloads, and error
  messages. Staff-only and machine-to-machine surfaces may be allow-listed, each entry with a written reason.
  Why: sequential IDs let anyone count records and diff growth month by month; a rule kept by convention alone was
  later found broken in an activity feed, in cursors and in a fallback expression. Test: the response-scanning
  guard below is green over the whole feature suite, and each egress channel it cannot see has its own payload
  test. Source: OWASP API Security Top 10 2023, API1 "How To Prevent": "Prefer the use of random and unpredictable
  values as GUIDs for records' IDs"
  (https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization, verified 2026-10-31);
  CWE-639 (https://cwe.mitre.org/data/definitions/639.html, verified 2026-10-31).
- [invariant] An opaque ID is not an authorization decision: every lookup by public ID still goes through tenant
  scoping and the permission check. Links that grant access by possession are a separate capability-token design
  with expiry, revocation and audit, never the record ID. Why: IDs leak through logs, referrers, screenshots and
  support tickets. Test: request a valid, existing public ID of another tenant's invoice; expect 404 and an
  unchanged row. Source: RFC 9562 §8: UUIDs "MUST NOT be used as security capabilities (identifiers whose mere
  possession grants access)" (https://www.rfc-editor.org/rfc/rfc9562.html, verified 2026-10-31).
- [invariant] Foreign, invisible, malformed and missing IDs look identical: the same status (404) and the same body
  shape on web and API. For IDs referenced inside a request body, all four produce the same validation error.
  Why: any difference turns the endpoint into an existence oracle for other tenants' records. Test: request a
  random well-formed ID that does not exist, a real foreign ID and a malformed ID; assert equal status and equal
  body after removing request-specific fields. Source: RFC 9110 §15.5.4: "An origin server that wishes to "hide"
  the current existence of a forbidden target resource MAY instead respond with a status code of 404 (Not Found)."
  (https://www.rfc-editor.org/rfc/rfc9110.html, verified 2026-10-31).
- [invariant] A response-scanning guard fails the build on any internal ID: a test-only hook in the base test case
  inspects every response the feature suite produces (JSON bodies, page props, decoded cursors, `Location`) and
  fails the producing test on an integer or digit-string value under `id`, `*_id` or `*_ids`. The allowlist is
  short and every entry has a reason. A self-test feeds each leak shape to the guard. Why: it checks every endpoint
  the suite exercises, including endpoints written after the rule. Test: temporarily emit the internal key in one
  serializer; the suite turns red. `python3 ${CLAUDE_SKILL_DIR}/scripts/scan_id_leaks.py --self-test` passes.
  Source: reproducible with the test above.
- [invariant] Translate at one boundary, with no fallbacks: serializers map `id` to the public ID and every
  reference field (`customer_id`) to the referenced record's public ID. Never write `public_id ?? id`; if a model
  has no public ID, add one first or omit the field. A hidden-attributes list is not the only protection. Why: the
  fallback leaks the internal key exactly for the records that lack a public ID. Test: the guard, plus a CI grep
  that fails on `public_id ??` and `publicId ??` in serializers. Source: reproducible with the test above.
- [invariant] Mint public IDs from a CSPRNG with an unbiased algorithm: `random_bytes` or `random_int` in PHP,
  `crypto.getRandomValues` in browsers and Node, `crypto/rand` in Go, `secrets` in Python, with rejection sampling or
  a library that documents uniformity. Never `mt_rand`, `Math.random`, `math/rand` or `random % alphabetLength`.
  Check which mode of an ID library you call: the default is not always the secure one. Why: a seeded PRNG's state
  can be recovered from its output, and modulo bias skews the distribution. Test: an arch rule that one generator
  class is the only place IDs are minted, plus a unit test of length and alphabet. Source: NanoID README:
  "`random % alphabet` is a popular mistake to make when coding an ID generator" (https://github.com/ai/nanoid,
  verified 2026-10-31); hidehalo/nanoid-php `Client::generateId()` defaults to `MODE_NORMAL`, whose
  `normalRandom()` calls `mt_rand()` (https://github.com/hidehalo/nanoid-php/blob/master/src/Client.php, verified
  2026-10-31).
- [invariant] The server mints public IDs; clients never choose them: generate the ID at creation, ignore or reject
  a client-supplied `public_id` or `id`, and keep the column out of mass assignment. Imports and offline clients
  that bring their own IDs store them in a separate tenant-scoped `external_id` column. Why: a client-chosen ID can
  be predictable, can collide, or can squat an ID another record needs. Test: create an invoice with a chosen
  `public_id`; the stored public ID differs from the supplied one. Source: reproducible with the test above.
- [invariant] Bind routes by public ID, and treat a malformed value as missing (404, not 422 or 500). When the
  alphabet changes, the shape check keeps accepting the old alphabet so stored links still resolve; existence and
  tenant are decided by the scoped lookup, never by the pattern. Why: a separate status for malformed input leaks
  the format, and a tightened pattern breaks old links. Test: malformed ID gives 404; an ID in the legacy alphabet
  still resolves. Source: reproducible with the test above; Laravel example in the stack reference.
- [invariant] Never cursor-paginate on the internal ID: order by non-sensitive columns with a unique tiebreaker,
  such as `(created_at, public_id)`. Why: the cursor carries the ORDER BY values and is only encoded, not
  encrypted. Test: decode a `next_cursor` from a list response; it holds no internal key. Source: laravel/framework
  12.x `Cursor::encode()` is `base64_encode(json_encode($this->toArray()))` with URL-safe replacements
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Pagination/Cursor.php, verified 2026-10-31).
- [invariant] Cover the egress channels an HTTP guard cannot see: broadcasts and channel names, mails, outbound
  webhooks, file exports and queued notifications each get a test that captures the real payload and runs the same
  key check. Name realtime channels by public ID. Why: these payloads never pass the HTTP test pipeline. Test: one
  test per channel type; feed the captured payload to `scan_id_leaks.py`. Source: reproducible with the test above.
- [invariant] Integers above 2^53 − 1 are strings in JSON for JavaScript clients, and every ID field in the API
  schema has `type: string`. Why: JavaScript numbers lose integer precision beyond `Number.MAX_SAFE_INTEGER`, so
  two different IDs can compare equal. Test: an OpenAPI lint rule over properties named `id` or ending in `_id`.
  Source: MDN, `Number.MAX_SAFE_INTEGER` is 2^53 − 1
  (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER,
  verified 2026-10-31).
- [default] Two keys: tables whose rows clients reference get a bigint identity primary key for every foreign key
  and join, plus a separate `public_id` column that is the only external identifier. Purely internal tables
  (pivots, ledgers) get no public ID. Trade-off: one extra column, one unique index and a translation step at the
  boundary, in exchange for 8-byte ordered joins and an external format that can change without touching foreign
  keys. Deviate only with an ADR that names this trade-off. Proof: a CI schema check that every table behind an
  API resource has a unique `public_id` and that every foreign key column is a bigint.
- [default] The public ID is a NanoID: 21 characters over the 62-character alphabet `0-9a-zA-Z` (no `-` or `_`, so
  an ID selects with a double-click), minted from a CSPRNG in the library's secure mode, about 125 bits
  (21 × log2 62). Trade-off: random IDs insert at scattered positions in the public-ID unique index (page splits,
  worse cache locality); time-ordered formats such as UUIDv7 and ULID insert sequentially but reveal each record's
  creation time and order. Deviate only with an ADR that names this trade-off; a time-ordered format is defensible
  only where creation time is already public. Source: RFC 9562 §5.7, UUIDv7 puts "a Unix timestamp in milliseconds
  in the most significant 48 bits" (https://www.rfc-editor.org/rfc/rfc9562.html); ULID spec, 48-bit millisecond
  time plus 80 random bits (https://github.com/ulid/spec); both verified 2026-10-31.
- [default] One unique constraint on `public_id`, no second plain index on it; index every bigint foreign key;
  lead composite tenant indexes with the bigint tenant column; keep public IDs globally unique, not per tenant.
  Trade-off: a global unique index costs one index entry per row across all tenants, in exchange for one ID
  meaning one record in logs and support. Deviate only with an ADR that names this trade-off. Source: PostgreSQL
  docs, Unique Indexes: "There's no need to manually create indexes on unique columns; doing so would just
  duplicate the automatically-created index." (https://www.postgresql.org/docs/current/indexes-unique.html,
  verified 2026-10-31).
- [default] Typed, prefixed handles on surfaces that people or agents read (CLIs, agent tools, support views):
  `inv_` plus the public ID. Accept the handle, the bare ID or a console link; reject a handle of the wrong kind
  with an error that names the right lookup; resolve only inside a tenant-scoped query. Trade-off: longer IDs and a
  parsing step, in exchange for precise errors when a caller mixes up IDs. Deviate only with an ADR that names this
  trade-off. Proof: a wrong-kind handle returns a 4xx naming the lookup; a foreign handle returns 404.
- [default] Retrofitting public IDs onto an API that exposes sequential IDs is an expand/contract migration: add a
  nullable column, backfill in batches, build the unique index concurrently and attach it as a constraint, switch
  serializers and route binding, then remove numeric routes after a deprecation window. Trade-off: two releases and
  a window in which old links still resolve. Deviate only with an ADR that names this trade-off. Source: PostgreSQL
  docs, ALTER TABLE `ADD CONSTRAINT ... UNIQUE USING INDEX`, used after `CREATE UNIQUE INDEX CONCURRENTLY`
  (https://www.postgresql.org/docs/current/sql-altertable.html, verified 2026-10-31).

## Procedure

1. Gate: does any client, mail, export or channel ever see this record? If not, it gets no public ID. If yes,
   continue.
2. Check the project overlay for a recorded format. Without an ADR, use the NanoID default.
3. Schema: bigint identity primary key, `public_id` with exactly one unique constraint, bigint foreign keys.
4. Generator: one class mints, validates the shape and defines length and alphabet. Confirm the library mode
   reaches `random_bytes` or an equivalent CSPRNG by reading its source at the installed version.
5. Model: public ID filled on create when empty, not mass-assignable, route key is `public_id`.
6. Serializers: `id` is the public ID; every reference field is the referenced record's public ID; no fallback.
7. Routes: bind by public ID through the tenant (see `tenant-isolation`); malformed returns 404.
8. Lists: cursor pagination ordered by `(created_at, public_id)` or another non-internal key.
9. Egress: payload tests for each mail, webhook, export and channel the change touches.
10. Run the guard over the suite and `scan_id_leaks.py` over captured payloads. Both are clean before review.

## Traps

- The ID library's default mode is not the secure one. In hidehalo/nanoid-php the default `generateId()` path uses
  `mt_rand()` while its docblock says "secure". Read the source at the installed version before trusting a mode.
- "UUID" in a framework helper is often time-ordered. In Laravel 12 and 13, `HasUuids` mints UUIDv7, and
  `HasVersion4Uuids` mints `Str::orderedUuid()`, whose docblock reads "Generate a time-ordered UUID". Neither hides
  creation time. Details in the stack reference.
- The same traits make the column they target the string primary key unless `uniqueIds()` points them at
  `public_id`, which silently gives up the two-key design.
- A fallback such as `public_id ?? id` passes every test whose fixtures all have public IDs.
- A cursor looks opaque in the URL and decodes to the sort columns.
- A schema template with both `unique()` and `index()` on the public ID gets copied into every new migration.
- Channel names carry IDs too, and they are visible in the browser's network log.
- Tightening the validation pattern after an alphabet change breaks links that are already stored in mails and
  bookmarks.

## Done when

- Every client-visible table has a bigint key and a uniquely constrained `public_id`, or an ADR says otherwise.
- The response-scanning guard runs in the base test case, its self-test is green, and a mutation turns it red.
- Each egress channel touched by the change has a payload test with the same key check.
- Paired tests show foreign, missing and malformed IDs return the same status and body shape.
- A create request with a chosen `public_id` does not keep it.
- No cursor, `Location` header or channel name contains an internal key.

## References

- [references/format-tradeoffs.md](references/format-tradeoffs.md): load when choosing or changing the ID format,
  when someone proposes UUIDv7 or ULID for index performance, or to write the ADR.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when building or extending the leak guard,
  adding an allowlist entry, writing egress-channel tests, or adding the duplicate-index and schema checks.
- [references/retrofit-migration.md](references/retrofit-migration.md): load when an existing API already exposes
  sequential IDs.
- [references/stack-laravel-postgres.md](references/stack-laravel-postgres.md): load when the project uses Laravel
  or PostgreSQL. The Laravel in-suite guard implementation belongs to `laravel-architecture`.
- `${CLAUDE_SKILL_DIR}/scripts/scan_id_leaks.py`: run over captured JSON or JSONL payloads (guard report output,
  webhook, mail, broadcast or export dumps). `--help` lists the options; `--self-test` proves it catches each leak
  shape.

## Sources

- https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization: object-level checks and
  unpredictable record IDs, verified 2026-10-31.
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html: "Avoid exposing identifiers to the
  user when possible", verified 2026-10-31.
- https://cwe.mitre.org/data/definitions/639.html: authorization bypass through a user-controlled key, verified
  2026-10-31.
- https://www.rfc-editor.org/rfc/rfc9562.html: §5.4 (UUIDv4, 122 random bits), §5.7 (UUIDv7 timestamp), §8
  (not hard to guess, not capabilities, timestamp signals creation order), verified 2026-10-31.
- https://www.rfc-editor.org/rfc/rfc9110.html: §15.5.4, 404 may hide a forbidden resource, verified 2026-10-31.
- https://github.com/ulid/spec: 48-bit millisecond time, 80 random bits, monotonic increment within one
  millisecond, verified 2026-10-31.
- https://github.com/ai/nanoid: 21 characters, 126 bits for the default alphabet, modulo bias, verified 2026-10-31.
- https://github.com/hidehalo/nanoid-php/blob/master/src/Client.php: default mode uses `mt_rand()`, verified
  2026-10-31.
- https://www.php.net/manual/en/function.random-int.php: "cryptographically secure, uniformly selected integer",
  verified 2026-10-31.
- https://www.postgresql.org/docs/current/indexes-unique.html: unique constraints create their index, verified
  2026-10-31.
- https://www.postgresql.org/docs/current/sql-altertable.html: `UNIQUE USING INDEX` after a concurrent build,
  verified 2026-10-31.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER: safe
  integer limit, verified 2026-10-31.
