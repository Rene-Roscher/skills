---
name: egress-and-webhooks
description: "Secures server-side requests to user-supplied URLs and webhooks both ways: SSRF defense with a pinned IP, IPv4 and IPv6 blocklists, connect-time and per-redirect checks; Standard Webhooks signing, secret rotation, retries and auto-disable; raw-body verification and dedup for incoming hooks; encrypted credentials. Use when fetching a URL a user typed or adding a webhook. Not for CORS."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Egress and webhooks

This skill decides how the server talks to addresses that users or partners control: URL monitors, outgoing
webhooks, imports by URL, link previews, avatar or feed fetchers, and webhooks that providers send in. HTTP client
syntax stays with the vendor docs and the stack references below. Retry mechanics for queued work in general belong
to `async-reliability`, payment webhook state machines to `billing-eu-b2b`, IDs in payloads to
`dual-key-identifiers`. The failure this prevents: a user-supplied URL or a followed redirect that reaches cloud
metadata, an internal admin panel or another tenant's network, and webhooks that can be forged, replayed or lost.

## Applies when / does not apply

- Applies: any server-side request whose host, path or redirect target a user, tenant or partner can influence;
  outgoing webhooks and their signing secrets; endpoints that receive webhooks from payment, mail, chat or
  identity providers; storage of integration credentials (API keys, bot tokens, webhook secrets).
- Does not apply: browser-side fetches and CORS, requests to fixed vendor hosts configured only by operators,
  inbound rate limiting of the public API (`api-contract`), payment state transitions after verification
  (`billing-eu-b2b`).

## Rules

Most important first. Examples use a booking app that pings customer URLs, sends booking events to customer
webhooks and receives payment and mail-bounce webhooks.

### Requests to user-supplied URLs

- [invariant] One egress client serves every user-supplied URL, and no other code path fetches one. Why: a second
  client added for one feature never gets the later fixes. Test: an architecture rule fails when a module outside
  the egress package constructs an HTTP client and passes it user input; a list of call sites is reviewed per
  change. Source: OWASP SSRF Prevention Cheat Sheet
  (https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html,
  verified 2026-11-03).
- [invariant] Resolve the host once, check every returned address, and connect to the pinned address; the
  hostname is used only for SNI and the `Host` header. Refuse a name whose answers mix public and blocked
  addresses. Why: validating a name and letting the client resolve it again leaves a DNS rebinding window. Test: a
  fake resolver returns a public address first and a loopback address second; no connection to loopback is
  attempted. Source: OWASP, "A second, unchecked DNS lookup between validation and connection can bypass these
  checks" (URL above, verified 2026-11-03).
- [invariant] Block every special-purpose range for IPv4 and IPv6, not only RFC 1918: loopback, private, shared
  address space (CGNAT), link-local including cloud metadata, "this network", reserved, broadcast, multicast,
  benchmarking, unique-local, IPv4-mapped and translated IPv6 (decode the embedded IPv4 and check it too), 6to4,
  Teredo, plus the operator's own cluster and VPC ranges. Why: library defaults often miss shared address space and
  the IPv6 forms that carry an IPv4 address. Test: a table-driven test with one address per range, including
  mapped and translated forms, each refused with its reason. Source: IANA IPv4 and IPv6 special-purpose address
  registries (https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml,
  https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml, verified
  2026-11-03).
- [invariant] Check again at connect time with a dial hook on the socket address the client actually uses. Why:
  proxies, retries, happy-eyeballs fallbacks and library code paths can open a connection that skipped the
  resolver check. Test: bypass the resolver step in a test and point the client at loopback; the dial hook
  refuses. Source: Go `net.Dialer.Control` "is called after creating the network connection but before actually
  dialing" (https://pkg.go.dev/net#Dialer, verified 2026-11-03).
- [invariant] Parse the URL once with one parser and reject what it cannot read unambiguously: schemes other than
  `http` and `https`, userinfo, control characters, numeric host forms (decimal, octal, hex), and ports outside the
  allowed list. Why: two parsers that read the same string differently let a URL pass the check and reach another
  host. Test: a table of parser-confusion inputs, each refused. Source: OWASP, "Reject a URL whose host is not read
  identically by every parser in play" (URL above, verified 2026-11-03).
- [invariant] Redirects are off, or capped at a small count with every hop passed through the same scheme, host,
  port and address checks. Why: a public URL that answers 302 to the metadata address is a full SSRF. Test: a
  public test server answers 302 to a loopback URL; the client refuses the hop. Source: OWASP, "Disable the support
  for the following of the redirection in your web client" (URL above, verified 2026-11-03).
- [invariant] Every request has connect and total timeouts, and the body is capped after decompression. Why: slow
  or endless responses tie up workers, and a small compressed body can expand without limit. Test: a server that
  sends one byte per second is cut at the total timeout; a compression bomb is cut at the decompressed cap. Source:
  reproducible with the test above.
- [invariant] The egress client sends no ambient credentials: no cookies, no internal service tokens, no cloud
  credentials, and users see a reason code instead of internal response bodies or network errors. Why: credentials
  sent to an attacker's URL are stolen, and detailed errors map the internal network. Test: capture a request to a
  test server; only the headers the feature defines are present; a refused URL returns the reason code only.
  Source: OWASP, "In cloud environments SSRF is often used to access and steal credentials and access tokens from
  metadata services" (URL above, verified 2026-11-03).
- [default] Egress for user URLs runs from workers whose network policy also denies private and metadata ranges,
  so the application guard is not the only layer. Trade-off: a separate worker pool and network policy to run.
  Deviate only with an ADR that names this trade-off. Source: OWASP cheat sheet, network layer protections (URL
  above, verified 2026-11-03).

### Outgoing webhooks

- [invariant] Sign per Standard Webhooks: headers `webhook-id`, `webhook-timestamp`, `webhook-signature`; `v1`
  is base64 HMAC-SHA256 over `id.timestamp.body`; the `webhook-id` stays the same across retries; the body sent is
  the stored body byte for byte; customer-defined headers cannot override the three. Why: receivers can verify,
  reject replays and deduplicate with off-the-shelf libraries. Test: verify a captured delivery with an official
  Standard Webhooks library; change one body byte and verification fails. Source: Standard Webhooks spec,
  "The content to be signed is therefore: `msg_id.timestamp.payload`" and "Use the `webhook-id` header as an
  idempotency key" (https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md,
  verified 2026-11-03).
- [invariant] Rotate secrets with overlap: during the rotation window, sign with every active secret and send all
  signatures in `webhook-signature`; the old secret expires at a set time. Secrets are `whsec_` prefixed, stored
  encrypted (they must be readable to sign), and shown in full only when created. Why: the receiver deploys the
  new secret at its own pace without dropped deliveries. Test: with two active secrets, a receiver holding either
  one verifies. Source: Standard Webhooks spec, "The reason it is a list, and not just one signature is to support
  zero downtime secret rotation" (URL above, verified 2026-11-03).
- [invariant] Deliveries go through the egress client with redirects off and a short timeout; only 2xx counts as
  delivered; retries back off exponentially over hours to days; an endpoint is disabled after persistent failure
  or on `410 Gone`, and its owner is told. Why: an endpoint that is down for a day must not lose events, and one
  that is gone must stop costing work. Test: an endpoint that fails N times is disabled and a notice is queued; a
  `410` disables it at once. Source: Standard Webhooks spec, "It's recommended to retry delivery following a retry
  schedule spanning multiple days, with an exponential backoff" and for `410` the sender "should disable the
  webhook endpoint" (URL above, verified 2026-11-03).
- [invariant] Each endpoint has a delivery log the tenant can see: event, webhook ID, attempt, time, status code,
  latency, a truncated response excerpt and next retry, with a manual resend that reuses the webhook ID. Why:
  "we never received it" is answered from the log, not from guesses. Test: a failed and a succeeded attempt both
  appear with status and latency; resend keeps the webhook ID. Source: reproducible with the test above.

### Incoming webhooks

- [invariant] Verify the signature over the raw request body before parsing, compare in constant time, and reject
  timestamps outside the tolerance. Why: re-serialized JSON changes bytes and breaks verification, a plain string
  compare leaks timing, and an old signed request can be replayed. Test: the same payload re-encoded fails; one
  flipped byte fails; a timestamp outside the window fails; a valid request passes. Source: Standard Webhooks spec,
  "use a constant time comparison function" (URL above); Stripe webhooks docs, verification needs the raw request
  body (https://docs.stripe.com/webhooks); both verified 2026-11-03.
- [invariant] Treat the body as a hint when it carries only IDs or when state matters: fetch the object from the
  provider with your own credentials and act on that. Unknown IDs get a success response and no effect. Why: an
  ID-only webhook has nothing to verify, and the fetch is the authentication. Test: post a made-up ID; 200, no
  state change, no error log at error level. Source: Mollie webhooks, "the Mollie API will always only send you an
  ID", and return `200 OK` "even if the ID is not known to your system" (https://docs.mollie.com/reference/webhooks,
  verified 2026-11-03).
- [invariant] Deduplicate with an insert-on-conflict on the provider's event ID, or on provider, object ID and
  transition when the provider has no event ID; store, answer 2xx, and process in a job. Why: providers redeliver,
  and a key on the object ID alone swallows a later refund or chargeback for the same payment. Test: the same
  event twice gives one row and one effect; a refund after a payment on the same object ID is processed. Source:
  Stripe webhooks docs, endpoints "occasionally receive the same event more than once" (URL above, verified
  2026-11-03).
- [default] Timestamp tolerance is 5 minutes, with clocks synced by NTP. Trade-off: a wider window accepts older
  replays, a narrower one rejects slow but valid deliveries. Deviate only with an ADR that names this trade-off.
  Source: Stripe webhooks docs, the libraries' default tolerance is 5 minutes and a tolerance of 0 disables the
  check; the Standard Webhooks spec names no value (URLs above, verified 2026-11-03).

### Credentials

- [invariant] Integration credentials (API keys, bot tokens, webhook secrets, OAuth tokens) are encrypted at rest
  with an application key, are write-only in API and UI (a fixed sentinel means "keep the stored value"), and
  never reach logs, error trackers or job payloads in plain text. Why: database dumps, logs and error-tracker
  frame arguments are read by more people than the secret's owner. Test: read the endpoint over the API and get
  the sentinel; trigger a provider error and assert the captured log and error event hold no secret. Source:
  reproducible with the test above.

## Procedure

1. Gate: can a user, tenant or partner influence the host, path or redirect target, or is this an inbound webhook?
   If neither, stop.
2. Route the request through the egress client; no new HTTP client for user input.
3. Confirm the client resolves once, pins, checks the full range table, re-checks at dial time and per hop.
4. Set redirects, timeouts, body cap after decompression, allowed ports and schemes.
5. For outgoing webhooks: Standard Webhooks headers, rotation list, delivery log, retry and disable policy.
6. For incoming webhooks: raw-body verification or re-fetch, tolerance, insert-on-conflict, 2xx, process in a job.
7. Store credentials encrypted, return the sentinel, scrub logs and error events.
8. Run the range table, rebinding, redirect, bomb and verification tests before review.

## Traps

- Library private-network filters differ: one widely used PHP filter's default subnet list omits shared address
  space (CGNAT), IPv4-translated IPv6 and 6to4. Read the list at your installed version.
- The metadata service also has hostnames (the OWASP table lists `metadata.google.internal`); refuse those names
  before resolving, not only the link-local address.
- A check on `parse_url()` output followed by a request built from the original string checks one host and fetches
  another.
- Go's default client follows up to 10 redirects; most HTTP clients follow redirects unless told not to.
- A framework that parses JSON before your controller hands you a re-encoded body; verification then fails at
  random, and someone "fixes" it by skipping verification.
- Retrying a webhook with a new `webhook-id` makes every receiver process it twice.
- Webhook secrets hashed like passwords cannot sign anything; they need reversible encryption.
- A health check that pings the user's URL from the web tier is still SSRF.

## Done when

- One egress client, an architecture rule enforcing it, and a range table test covering IPv4, IPv6 and mapped forms.
- Rebinding, redirect-to-loopback, slow-body and compression-bomb tests pass.
- Outgoing deliveries verify with a Standard Webhooks library, rotate with overlap, log every attempt, and
  disable on persistent failure or `410`.
- Incoming handlers verify on the raw body in constant time or re-fetch, deduplicate with insert-on-conflict and
  return 2xx after storing.
- Credentials are encrypted, write-only, and absent from logs and error events.

## References

- [references/ssrf-guard.md](references/ssrf-guard.md): load when building or reviewing the egress client, its
  range table, URL canonicalization or tests.
- [references/webhooks.md](references/webhooks.md): load when implementing signing, rotation, the retry and
  disable policy, the delivery log, or an inbound webhook handler.
- [references/stack-laravel-go.md](references/stack-laravel-go.md): load when the egress client is built on Laravel
  (Guzzle or Symfony HttpClient) or Go `net/http`.

## Sources

- https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html:
  rebinding, redirects, metadata, minimum ranges, parser differences, verified 2026-11-03.
- https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml: IPv4
  special-purpose blocks, verified 2026-11-03.
- https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml: IPv6
  special-purpose blocks, verified 2026-11-03.
- https://pkg.go.dev/net#Dialer: `Control` runs before dialing, verified 2026-11-03.
- https://pkg.go.dev/net/http#Client: default redirect policy stops after 10 requests, verified 2026-11-03.
- https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md: headers, signed
  content, rotation, retries, disabling, constant-time comparison, verified 2026-11-03.
- https://docs.stripe.com/webhooks: raw body, 5-minute default tolerance, duplicates, verified 2026-11-03.
- https://docs.mollie.com/reference/webhooks: ID-only body, 200 for unknown IDs, verified 2026-11-03.
- https://github.com/symfony/symfony/blob/7.3/src/Symfony/Component/HttpFoundation/IpUtils.php: default
  `PRIVATE_SUBNETS` list, verified 2026-11-03.
