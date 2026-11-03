# Laravel and Go egress

Load when the egress client is built on Laravel (Guzzle or Symfony HttpClient) or Go `net/http`. Facts read
2026-11-03; re-check them at your installed versions.

## Laravel and PHP

- Laravel's `Http` client wraps Guzzle and has no private-network guard of its own. Wrap user-URL requests in one
  service class; an architecture test forbids `Http::` calls with user input elsewhere.
- Symfony `NoPrivateNetworkHttpClient` checks the resolved IP, and its source re-checks the `primary_ip` during
  transfer, which also covers the redirect hops it follows. With no subnet argument it uses
  `IpUtils::PRIVATE_SUBNETS` plus PHP's private and reserved range flags. In the 7.3 branch that list has loopback, RFC 1918, link-local, `0.0.0.0/8`, <!-- lint-allow: L13 ranges quoted from the Symfony source -->
  `240.0.0.0/4`, `::1`, `fc00::/7`, `fe80::/10`, `::ffff:0:0/96` and `::/128`. Pass the full range table from
  `ssrf-guard.md` as the subnet argument so shared address space, translated IPv6 and 6to4 are covered
  (https://github.com/symfony/symfony/blob/7.3/src/Symfony/Component/HttpClient/NoPrivateNetworkHttpClient.php,
  https://github.com/symfony/symfony/blob/7.3/src/Symfony/Component/HttpFoundation/IpUtils.php).
- Symfony HttpClient follows up to 20 redirects by default; set `max_redirects` to 0 or a small number. Use
  `timeout` (idle) and `max_duration` (whole request) together (https://symfony.com/doc/current/http_client.html).
- Encrypted credentials: Eloquent `encrypted` and `encrypted:array` casts; the API resource returns a fixed
  sentinel for these fields and the update path ignores the sentinel.
- Incoming verification: read `$request->getContent()` for the raw body, compare with `hash_equals()`.
- Error trackers: disable capture of stack frame arguments or scrub them, since a secret passed as an argument
  appears there.

## Go

- Resolve with a `net.Resolver` using the Go resolver, check every address, then dial the pinned IP through a
  custom `DialContext`.
- Add `net.Dialer.Control` (or `ControlContext`) as the connect-time check; the Go docs say it runs "after creating
  the network connection but before actually dialing" (https://pkg.go.dev/net#Dialer).
- `http.Client.CheckRedirect`: the default policy stops after 10 requests; return `http.ErrUseLastResponse` to
  stop at the first redirect, or run the guard for each hop (https://pkg.go.dev/net/http#Client).
- Set `Client.Timeout` plus transport `TLSHandshakeTimeout` and `ResponseHeaderTimeout`.
- Cap bodies with `io.LimitReader` placed after the decompressor; read limit plus one byte to detect overflow.
- Keep the guard in one internal package with a typed reason enum and table tests; fuzz the URL parser input.
