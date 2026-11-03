# Edge config, container and CI

## Contents

- Global options and headers
- Rate limit, error pages and cache
- Container
- CI

## Global options and headers

```caddyfile
{
	admin off
	servers {
		trusted_proxies static 192.0.2.0/24     # the load balancer range, nothing wider
		client_ip_headers X-Forwarded-For
		trusted_proxies_strict
	}
	order rate_limit before reverse_proxy
}
```

`admin off` makes config changes impossible without a restart; that is the point on an edge that is deployed by
replacing files. With PROXY protocol from the load balancer, use the listener wrapper for it instead of trusting
headers, and enable it on both sides in the same change.

Upstream headers: Caddy already sets `X-Forwarded-For`, `X-Forwarded-Proto` and `X-Forwarded-Host` and ignores
incoming values from untrusted peers. If the next hop is another proxy, make sure that hop forwards them only from
the edge's range and does not overwrite the scheme with its own `http`.

## Rate limit, error pages and cache

```caddyfile
(protect) {
	request_body {
		max_size 1MB
	}
	request_header -Cache-Control
	request_header -Pragma
	rate_limit {
		zone per_client {
			key {client_ip}
			events 120
			window 1m
		}
		zone per_prefix {
			key {client_ip}
			ipv4_prefix 24
			ipv6_prefix 48
			events 600
			window 1m
		}
	}
	handle_errors {
		@limited expression {err.status_code} == 429
		handle @limited {
			header Cache-Control "no-store"
			respond "Too many requests from your network. Try again in a minute." 429
		}
	}
}
```

The prefix lengths and counts are placeholders; derive them from real peak traffic per address. `rate_limit`
requires the plugin, so CI asserts `http.handlers.rate_limit` in `caddy list-modules`.

Origin headers for public pages, set by the app per response:

```text
Cache-Control: public, max-age=30, stale-while-revalidate=60, stale-if-error=86400
```

Everything else: `Cache-Control: no-store` or `private`. Error pages from the edge (502, 503, 504, 429): `no-store`.
If the edge runs a cache module, confirm in a test that it honours `stale-if-error`; support differs between
modules.

Upstream behaviour: `lb_try_duration` of a few seconds, passive health checks with `fail_duration`,
`unhealthy_latency` and `unhealthy_request_count` so a slow origin is shed instead of queueing every request.

## Container

```yaml
services:
  edge:
    image: registry.example.com/edge/caddy@sha256:[digest]
    user: "10001:10001"
    read_only: true
    tmpfs:
      - /tmp
    cap_drop: [ALL]
    cap_add: [NET_BIND_SERVICE]
    security_opt:
      - no-new-privileges:true
    mem_limit: 1g
    environment:
      GOMEMLIMIT: 800MiB
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"     # only if the firewall opens UDP 443; otherwise disable HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
```

If ports 80 and 443 are bound by a non-root user, the binary needs `NET_BIND_SERVICE` from `cap_add`, or bind
high ports and map them. A binary that carries file capabilities can fail to start once capabilities are dropped;
test the final image with these exact settings, and strip file capabilities in the build if the image does not
need them.

## CI

```bash
img=registry.example.com/edge/caddy@sha256:[digest]
docker run --rm -v "$PWD/Caddyfile:/etc/caddy/Caddyfile:ro" -e ASK_SECRET=ci-dummy "$img" \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker run --rm "$img" caddy list-modules | grep -qx 'http.handlers.rate_limit'
```

Pin the base image and every plugin version, bump them as one group, and run the build without network-time
dependency resolution (no `go mod tidy` inside the image build).

## Two edges

Active and passive: unicast VRRP on cloud networks, a health check that requests a real page through the local
edge, a timeout counted as failure, no automatic failback. Bring the edge up and healthy before the failover
daemon starts. Details of failure domains and drills: `high-availability`.
