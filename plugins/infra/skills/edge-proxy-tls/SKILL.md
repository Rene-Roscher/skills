---
name: edge-proxy-tls
description: "Designs and reviews a Caddy edge: on-demand TLS for customer domains gated by an ask endpoint without secrets in the URL, trusted proxies and X-Forwarded-* handling, real client IPs, rate limits, cache headers with stale-if-error, a hardened edge container, caddy validate in CI and two edges. Use when editing a Caddyfile or custom-domain TLS. Not for in-cluster ingress or CDN setup."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/Caddyfile*"
  - "**/*.caddyfile"
  - "**/xcaddy*"
---

# Edge proxy and TLS

This skill decides how the public edge terminates TLS for the product's own domains and for customer domains,
which forwarded headers it trusts, how it protects the origin, and how its config is proven before it ships. The
examples use Caddy; the header, cache and container rules hold for any reverse proxy. Caddy syntax stays with the
Caddy docs; failover of the edge pair belongs to `high-availability`. The failure this prevents: an edge that
issues certificates for any name an attacker sends, leaks its gate secret into logs, builds `http://` redirects
behind TLS, falls over under a flood and runs as root on the host network.

## Applies when / does not apply

- Applies: a Caddyfile or Caddy JSON config; custom domains for customers (status pages, shops, white-label
  apps); the endpoint that approves certificate issuance; trusted proxy and client IP settings in the edge or
  the app behind it; rate limits, cache headers and error pages at the edge; the edge's container or service unit;
  CI for the edge image.
- Does not apply: Kubernetes Ingress or Gateway objects inside the cluster, a managed CDN's own config,
  certificate questions for internal mTLS, DNS failover (`high-availability`), application-level throttling.

## Rules

### On-demand TLS

- [invariant] `on_demand` is enabled only together with an `ask` endpoint (or a `permission` module), and the
  endpoint returns 2xx only for domains a customer added and verified. Every other case, including an internal
  error, returns a non-2xx status. Why: Caddy's docs say "On-demand TLS must be both enabled and restricted to
  prevent abuse"; an endpoint that fails open issues certificates for any name pointed at the edge. Test: ask for
  a random domain, a pending domain, and a verified domain with the database unreachable; only the verified
  domain with a working database gets 2xx. Source: https://caddyserver.com/docs/automatic-https and
  https://caddyserver.com/docs/caddyfile/options (`?domain=` query, 2xx authorizes), verified 2026-11-03.
- [invariant] The ask endpoint is reachable only on a private network or loopback, and a shared secret, if used,
  is never part of the URL. Put it in a request header added by a loopback-only Caddy site that proxies to the
  app, compare it in constant time, and fail closed when the secret is unset. Why: query strings end up in access
  logs, error trackers and config dumps; the ask URL is part of the config. Test: the config's `ask` URL contains
  no `secret=`, `token=` or `key=`; a request without the header and an app with an empty secret both get 403.
  Source: reproducible with the test above; pattern in
  [references/on-demand-tls.md](references/on-demand-tls.md).
- [invariant] Issuance has its own limits, because Caddy's `interval` and `burst` options "are NOT recommended":
  the ask route is throttled, answers are cached briefly (negatives shorter than positives), the lookup is a
  constant-time indexed query without DNS or network calls, and a breaker stops new orders when failed ACME
  attempts exceed a budget. Why: a flood of distinct SNI names otherwise hammers the app and burns CA rate limits.
  Test: 1,000 handshakes with random names under a customer suffix produce no ACME order and stay within the
  throttle at the app. Source: https://caddyserver.com/docs/caddyfile/options (ask "should return as fast as
  possible", deprecated rate options), verified 2026-11-03.
- [invariant] All edges share one certificate storage, so a failover or a new node reuses existing certificates.
  Why: "Any Caddy instances that are configured to use the same storage will automatically share those resources
  and coordinate certificate management as a cluster"; separate storage re-issues every certificate on failover.
  Test: fail over to the second edge; its log shows no new orders for known domains. Source:
  https://caddyserver.com/docs/automatic-https, verified 2026-11-03.
- [invariant] The certificate actually served is monitored from outside: expiry and issuer for the product's
  wildcard and for one synthetic customer domain the product owns. Why: renewals can fail silently for days while
  the old certificate still works. Test: a blackbox probe alerts at a set number of days before expiry. Source:
  reproducible with the test above.

### Forwarded headers and client IP

- [invariant] Trust `X-Forwarded-*` only from listed proxy ranges: `trusted_proxies` (by default "no proxies are
  trusted"), `client_ip_headers`, and `trusted_proxies_strict` for right-to-left parsing. Why: the docs warn that
  "the left-most IP address may be spoofed by the client". Test: send `X-Forwarded-For: [documentation address]`
  directly to the edge; the access log shows the real peer address. Source:
  https://caddyserver.com/docs/caddyfile/options and
  https://caddyserver.com/docs/caddyfile/directives/reverse_proxy, verified 2026-11-03.
- [invariant] Behind the edge, nobody trusts the forwarded scheme and port blindly. The edge sets
  `X-Forwarded-Proto: https` for TLS sites; a second proxy hop (an in-cluster ingress) either passes the edge's
  headers through for the edge's address range only, or the app derives the public scheme from its configured base
  URL; nginx-based hops use `absolute_redirect off`. Why: a hop that receives plain HTTP from the edge reports
  `http` and port 80, and the app then emits `http://` redirects, canonical URLs and `:80` links that search
  engines index. Test: `curl -sI https://[host]/[path that redirects]` returns a relative or `https://` Location
  without a port, and the canonical tag is `https`. Source: https://nginx.org/en/docs/http/ngx_http_core_module.html
  (`absolute_redirect`, `port_in_redirect`) and
  https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/ (`use-forwarded-headers`
  default false), verified 2026-11-03.
- [invariant] The real client IP reaches the app before any rate limit or audit log relies on it: PROXY protocol
  turned on at the load balancer and the receiver in the same change, or forwarded headers with trusted ranges.
  Why: with SNAT every request carries the balancer's address, so one client's limit blocks everyone. Test: a
  request from a known address appears with that address in the app log. Source: reproducible with the test above.

### Protecting the origin

- [invariant] Rate limit per client address and per prefix (IPv4 /24, a short IPv6 prefix) at the edge, before
  the cache, with a distinct 429 page marked `Cache-Control: no-store`. Caddy needs a plugin for this (for example
  `caddy-ratelimit`, built with `xcaddy`), so CI checks that the module is in the binary. Why: a distributed flood
  on an uncacheable URL can take the edge down, and a cached 429 serves the limit to everyone. Test: a burst from
  one address gets 429, a second address is unaffected, and the 429 carries `no-store`. Source:
  https://github.com/mholt/caddy-ratelimit (not built in, `ipv4_prefix`, `ipv6_prefix`, shared state), verified
  2026-11-03.
- [default] Request hygiene at the edge: drop client `Cache-Control`, `Pragma` and `Authorization` before the
  cache on public pages, cap request body size, answer 404 for internal paths, keep the upstream retry window
  (`lb_try_duration`) short, and use passive health checks (`unhealthy_latency`, `unhealthy_request_count`) to shed
  load. Trade-off: some clients lose the ability to force a refresh. Deviate only with an ADR that names this
  trade-off. Source: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy, verified 2026-11-03.

### Caching public pages

- [invariant] The origin decides cacheability per response with `Cache-Control`; anything unmarked is `no-store`.
  Responses that depend on a session, cookie or token are never shared-cached. Why: a cache that guesses serves one
  user's page to another. Test: a logged-in response carries `private` or `no-store` and the edge does not store
  it. Source: reproducible with the test above.
- [invariant] Public pages carry `stale-if-error` (and `stale-while-revalidate` where freshness allows), and error
  responses (5xx, 429) are `no-store` so they never replace the last good copy. Why: during an origin outage the
  edge keeps serving the last good page; RFC 5861 says a stale response "MAY be used to satisfy the request,
  regardless of other freshness information". Test: stop the origin; a cached page is still served with an `Age`
  header beyond its max-age. Source: https://www.rfc-editor.org/rfc/rfc5861.html, verified 2026-11-03.

### The edge itself

- [invariant] The edge container does not run as root on the host network. It runs as a non-root user, adds back
  only `NET_BIND_SERVICE` (or binds high ports behind a port mapping), uses `read_only: true` with tmpfs for
  writable paths, `cap_drop: [ALL]`, `no-new-privileges`, a hard memory limit with the Go heap limit
  (`GOMEMLIMIT`) below it, and the admin endpoint off or on loopback. Why: a compromised edge on the host network
  as root owns the host; a flood that grows memory without a limit takes the whole VM. Test: `docker inspect`
  shows a non-root user, `ReadonlyRootfs: true` and `CapDrop: [ALL]`; writing to `/` inside fails. Source:
  https://docs.docker.com/reference/compose-file/services/ (`read_only`, `cap_drop`, `security_opt`, `mem_limit`),
  verified 2026-11-03.
- [invariant] CI validates the config with the exact image that ships: `caddy validate` inside the pinned image,
  plus `caddy list-modules` to assert every module the config uses. Why: validate "loads and provisions all of its
  modules", which `caddy adapt` does not, and a module missing from the build fails only at start. Test: remove the
  rate limit module from the build; CI fails. Source: https://caddyserver.com/docs/command-line, verified
  2026-11-03.
- [default] Two edges in separate failure domains, active and passive behind a floating address or both behind
  DNS, with a health check that tests real serving and treats a check timeout as a failure; roll out one edge at a
  time, passive first. Trade-off: a second machine and a failover component to maintain. Deviate only with an ADR
  that names this trade-off. Test: stop and separately freeze (`SIGSTOP`) the active edge; traffic moves within the
  stated RTO both times. Source: reproducible with the test above; failure-domain rules in `high-availability`.

## Procedure

1. Gate: find the config that is actually deployed (trace the rollout), not a copy in another directory.
2. Walk the rules: on-demand TLS, headers and client IP, origin protection, caching, the edge container.
3. Load the reference that matches the change.
4. Validate in the pinned image (`caddy validate`, `caddy list-modules`) and test with `curl -sI` against a
   staging edge: redirects, canonical, cache headers, 429 page, ask responses.
5. Report the diff and the test results. Roll out passive first; do not apply from this skill.

## Traps

- The ask secret as a query parameter, which then shows up in every access log line of the app.
- An ask endpoint that returns 200 when its cache or database is down.
- `interval` and `burst` left in the config as the only issuance limit.
- A rate limit block commented out because nobody checked whether the module is in the image.
- An ingress that reports `X-Forwarded-Proto: http` to the app, found only when search results show `http://`.
- A cached 429 or 503 page that replaces the last good copy.
- A binary with file capabilities in an image whose capabilities are all dropped: it can fail to start. Test the
  final image with the final security settings.
- A health check script that times out and is skipped, so a frozen edge keeps the floating address.

## Done when

- The ask endpoint is private, fails closed, has no secret in its URL, and is throttled and cached.
- All edges share certificate storage, and served certificates are monitored from outside.
- Forwarded headers are trusted only from listed ranges; redirects and canonicals are `https` without a port.
- Rate limits answer 429 with `no-store`; public pages have `stale-if-error`.
- The edge runs non-root, read-only, with dropped capabilities and a memory limit.
- CI validates the config in the shipped image, and failover between two edges was tested.

## References

- [references/on-demand-tls.md](references/on-demand-tls.md): load when building or reviewing the ask endpoint,
  the issuance limits, shared storage or wildcard certificates.
- [references/edge-config.md](references/edge-config.md): load when writing the Caddyfile for headers, rate limits,
  caching and error pages, or the container and CI setup.

## Sources

- https://caddyserver.com/docs/automatic-https: on-demand TLS restriction, ask endpoint, shared storage, verified
  2026-11-03.
- https://caddyserver.com/docs/caddyfile/options: `on_demand_tls`, `trusted_proxies`, `client_ip_headers`,
  `trusted_proxies_strict`, `admin off`, verified 2026-11-03.
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy: forwarded headers, health checks,
  `lb_try_duration`, verified 2026-11-03.
- https://caddyserver.com/docs/command-line: `validate`, `adapt`, `list-modules`, verified 2026-11-03.
- https://github.com/mholt/caddy-ratelimit: rate limit module, verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc5861.html: `stale-while-revalidate`, `stale-if-error`, verified 2026-11-03.
- https://nginx.org/en/docs/http/ngx_http_core_module.html and
  https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/: redirect and forwarded
  header settings, verified 2026-11-03.
- https://docs.docker.com/reference/compose-file/services/: container hardening options, verified 2026-11-03.
