# Content Security Policy

How to reach a script policy without `'unsafe-inline'` on both surfaces. Header and module syntax is in the
vendor docs; this file keeps the decisions and the checks.

## What the browser does

- A `script-src` that contains a nonce or a hash does not allow all inline script, so `'unsafe-inline'` next to
  it has no effect in CSP Level 3 browsers (https://www.w3.org/TR/CSP3/, algorithm "Does a source list allow all inline behavior for type?", verified
  2026-10-31).
- The server generates a unique nonce each time it transmits a policy (CSP3, "Nonce Reuse"). MDN: generate it with
  a cryptographically secure random generator, unique for each HTTP request
  (https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src,
  verified 2026-10-31).
- `'strict-dynamic'` passes trust from a nonce- or hash-approved script to the scripts it loads, and makes the
  browser ignore host allowlists, `'self'` and `'unsafe-inline'` (MDN, same page).

## Policy per output type

| Output | Script authorization | Notes |
|---|---|---|
| Server-rendered response (SSR, Blade, Inertia root view) | `'nonce-...'` fresh per response, plus `'strict-dynamic'` | the nonce is attached to every script tag the framework emits |
| Prerendered HTML, ISR/SWR or CDN-cached HTML | `'sha256-...'` hashes of inline scripts, plus `'strict-dynamic'` | a nonce baked into cached HTML is a reused nonce |
| Dev server with HMR | separate, looser policy | never shipped; production builds get the strict one |

Every policy also carries `object-src 'none'`, `base-uri 'none'` (or `'self'`), `frame-ancestors` and
`form-action`.

## Nuxt

The nuxt-security module documents nonces for SSR only and hashes for SSG only (`ssg.hashScripts`); its default
`script-src` lists `'unsafe-inline'` as a fallback that modern browsers ignore, and its default `style-src`
keeps `'unsafe-inline'` as recommended for most Nuxt apps. It also has a top-level `strict` mode. Source:
https://nuxt-security.vercel.app/headers/csp and the module's configuration docs (verified 2026-10-31).

The docs do not say how nonces behave on ISR or SWR routes. Check it yourself: request the same cached page
twice and compare the nonce in the header and the HTML. If both responses carry the same nonce, move that route
to hashes or to output without inline scripts.

## Laravel and Vite

For a Laravel dashboard, generate the nonce per request in middleware with `Vite::useCspNonce()` and send the
header with `Vite::cspNonce()`. Laravel then adds the nonce to every script and style tag that `@vite`
generates. Inline scripts you write yourself take `nonce="{{ Vite::cspNonce() }}"`. Source:
https://laravel.com/docs/12.x/vite#content-security-policy-csp-nonce (verified 2026-10-31).

Register the CSP middleware where it also wraps error responses. A 404 for an unknown path never reaches
route-group middleware, so test that path explicitly.

## Styles

`style-src 'unsafe-inline'` is tolerated when the framework injects styles at runtime. The cost: injected CSS
can still exfiltrate data through image requests, so restrict `img-src` (and `font-src`) to the hosts you need.

## Rollout

1. Ship the policy as `Content-Security-Policy-Report-Only` with a reporting endpoint.
2. Fix the violations it reports on every page type.
3. Switch to the enforcing header, keeping the report endpoint.

## Checks

- CI against the built preview: the header is present on a 200, a 404 and a 500; `script-src` contains
  `'nonce-` or `'sha`; `'unsafe-inline'` never appears in `script-src` without one of them.
- Browser test: register a listener before navigation and assert zero events after the page settles.

```ts
await page.addInitScript(() => {
  (window as any).__cspViolations = []
  document.addEventListener('securitypolicyviolation', (e) => {
    (window as any).__cspViolations.push({ directive: e.violatedDirective, blocked: e.blockedURI })
  })
})
// ... navigate and interact, then:
expect(await page.evaluate(() => (window as any).__cspViolations)).toEqual([])
```

## Traps

- Error responses are a common gap: a page rendered outside the hook that sets headers ships without a CSP.
- A nonce in prerendered or edge-cached HTML is the same for every visitor.
- Keep the dev and production policies in separate code paths and assert the production one in CI, so the looser
  dev policy cannot ship.
