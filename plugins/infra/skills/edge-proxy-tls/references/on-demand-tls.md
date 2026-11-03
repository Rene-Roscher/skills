# On-demand TLS for customer domains

## Ask gate without a secret in the URL

Caddy calls the ask URL with `?domain=[name]` and accepts any 2xx. The URL is static config, so keep the secret
out of it: a loopback-only site in the same Caddy adds the secret as a header and forwards to the app's private
address.

```caddyfile
{
	on_demand_tls {
		ask http://localhost:9180/check
	}
}

http://localhost:9180 {
	bind localhost
	rewrite * /internal/tls/check?{query}
	reverse_proxy app.internal.example:8080 {
		header_up X-Edge-Ask-Secret {env.ASK_SECRET}
	}
}

https:// {
	tls {
		on_demand
	}
	reverse_proxy app.internal.example:8080
}
```

The public site must answer 404 for `/internal/tls/*`, so the check route is reachable only through the loopback
site. The app's private listener also checks that the request came in on the internal port.

App side, in this order:

1. Secret unset in the app config: 403. Header missing or wrong (constant-time compare): 403.
2. Throttle per edge address.
3. Normalize the name: lower case, strip a trailing dot, reject IP literals and names longer than 253 characters.
4. Cache lookup: positive answers for about an hour, negative answers for about a minute.
5. On cache miss, one indexed query for a domain in state "verified". On any error: non-2xx, never allow.
6. Breaker: when failed ACME orders, globally or per name, exceed the budget in a window, answer non-2xx for new
   names until the window passes, and alert.

Verification before "verified": the customer proves control (a CNAME to the product's target or a TXT token), and
the app checks it from more than one resolver.

## Shared storage

All edges use the same storage module (a database or key-value store with persistence and no eviction, its own
key prefix, encryption at rest if the module supports it). Proof: after a failover, the new edge logs no orders
for known domains.

## Wildcards for the product's own subdomains

Issue them with DNS-01 through a delegated zone (a CNAME from `_acme-challenge.[zone]` to a small zone used only
for challenges), with an API credential limited to that zone. Set the propagation wait longer than the zone's
negative-caching TTL from its SOA, and check propagation against several public resolvers. Keep port 80 open if a
fallback CA uses HTTP-01.

## Monitoring

- Blackbox probe on the socket for the wildcard and for one synthetic customer domain that the product owns (not a
  real customer's name, which can be deleted): days to expiry, issuer, chain.
- Counter of ask answers by result and of ACME failures; alert on a rising deny rate and on any breaker trip.
