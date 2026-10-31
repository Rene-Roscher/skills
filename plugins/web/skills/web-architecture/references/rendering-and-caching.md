# Rendering and caching

Pick the rendering mode per route class, then let one pure function decide the cache header. Route rule syntax
is in the Nuxt docs (https://nuxt.com/docs/4.x/guide/concepts/rendering, verified 2026-10-31). This file keeps
the decisions.

## Route classes

| Route class | Mode | Why |
|---|---|---|
| Static marketing, legal, company pages | prerender at build | no origin work per view, survives origin outages |
| Docs, blog, changelog | prerender, or ISR/SWR if content changes between deploys | fresh enough without a rebuild per edit |
| Pages that differ per visitor (account area on the public site, previews) | server render, `private, no-store` | personalized output must not be shared |
| Dashboard behind login (product app) | client render, SSR off | nothing to index, no SSR process to run |
| Root path `/` with locale detection | redirect, `no-store` | the redirect depends on the visitor |

Server rendering is the exception on a public site. Each SSR route needs a reason in the route table.

## The cache decision function

Keep every `Cache-Control` decision in one pure function with a unit table. Inputs: route class, status code,
whether the request is authenticated or personalized, whether the response sets a cookie. Output: the header.

```ts
// server/utils/cache-decision.ts (sketch; adapt names to your project)
export type RouteClass = 'static' | 'content' | 'personal' | 'redirect-root'

export function cacheControl(rc: RouteClass, status: number, personal: boolean, setsCookie: boolean): string {
  if (personal || setsCookie || rc === 'personal' || rc === 'redirect-root') return 'private, no-store'
  if (status !== 200) return 'no-store'
  if (rc === 'static') return 'public, max-age=0, s-maxage=3600, stale-while-revalidate=86400, stale-if-error=86400'
  return 'public, max-age=0, s-maxage=300, stale-while-revalidate=3600, stale-if-error=86400'
}
```

The numbers are examples. The structure is the rule: private by default, no caching of errors or per-visitor
redirects, no shared caching when a cookie is set.

Unit table rows to keep:

| Route class | Status | Personal | Sets cookie | Expected |
|---|---|---|---|---|
| static | 200 | no | no | `public ... s-maxage` |
| static | 404 | no | no | `no-store` |
| static | 503 | no | no | `no-store` |
| content | 200 | yes | no | `private, no-store` |
| content | 200 | no | yes | `private, no-store` |
| redirect-root | 302 | no | no | `private, no-store` |

## Header meanings

- `s-maxage`: freshness for shared caches (CDN). `max-age=0` keeps browsers revalidating.
- `stale-while-revalidate`: a cache may serve the stale response for that many seconds while it refetches.
- `stale-if-error`: a cache may serve a stale response when the origin errors. Use it where availability matters
  more than freshness.

Source: https://www.rfc-editor.org/rfc/rfc5861 (verified 2026-10-31).

- `Vary`: `Accept-Encoding` only. Varying on `Cookie` or `Accept-Language` splits the cache per visitor; put the
  locale in the path instead.

## CI header check

Run against the built preview, not the dev server:

```sh
#!/bin/sh
set -eu
base="${PREVIEW_URL:?set PREVIEW_URL}"
hdr() { curl -s -o /dev/null -D - "$base$1" | tr -d '\r'; }

hdr /pricing | grep -qi '^cache-control:.*s-maxage' || { echo "pricing not cacheable"; exit 1; }
hdr /pricing | grep -qi '^set-cookie:' && { echo "cacheable page sets a cookie"; exit 1; }
hdr /does-not-exist | grep -qi '^cache-control:.*no-store' || { echo "404 is cacheable"; exit 1; }
echo "cache headers ok"
```

Add a row for every route class in the table above.

## Traps

- A session or locale cookie on public responses made every response uncacheable, and the CDN reported no
  error. Check for `Set-Cookie` on a cacheable page in CI.
- A cached 404 or 503 shadowed the last good page until the TTL ran out. Errors get `no-store`.
- An ISR or SWR route that inlines a CSP nonce reuses that nonce for every visitor. Cached routes use hashes;
  see the CSP rule.
