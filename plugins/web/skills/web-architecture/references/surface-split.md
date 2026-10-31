# Surface split

Which web surface lives where, and how to argue the split in review.

## Where each surface lives

| Surface | Lives in | Renders | Cache |
|---|---|---|---|
| Marketing, product, pricing pages | public site | prerendered | shared, `s-maxage` + `stale-while-revalidate` |
| Docs, changelog, blog | public site | prerendered or ISR/SWR | shared |
| Company and legal pages (imprint, privacy, terms) | public site | prerendered | shared |
| Login, password reset, invitation accept | product app | server or client | `private, no-store` |
| Dashboards and settings behind login | product app | client-rendered Inertia, SSR off | `private, no-store` |
| Webhooks and public API | product app | none (JSON) | `no-store` unless the API defines caching |
| Status pages and embeds with live product data | separate decision | not covered here | not covered here |

## The argument in review

Use these reasons. They hold up:

1. Failure domain. The product runtime gets stopped or frozen: an emergency patch of the language runtime, a
   database migration, an incident, a bad deploy. A site in the same runtime goes down with it, at the moment
   prospects and customers come to read about the outage or the product.
2. Release cadence. Copy, pricing and docs change on a marketing schedule. Product releases follow their own.
   Neither should wait for the other's pipeline.
3. Caching. Prerendered pages behind a CDN keep serving when the origin is slow or down, and cost nothing per
   view.
4. SEO stability. URLs, canonical tags, `hreflang` and headers stay the same across product releases. A
   product refactor cannot drop a marketing route.

Do not argue with framework or language speed. It does not survive review and it is not the reason.

## What the public site may take from the product

- Build-time data (plan list, feature matrix, changelog entries) through an API call during the build, with a
  committed or last-good fallback so a product outage never breaks the site build.
- Links to the app's login and signup URLs.
- A shared component package or design tokens as a build dependency. Share code, not a runtime.

What it may not take: a runtime request to the product to render a page, the product's session, or the
product's database.

## Cookies across the two

Keep the app's session cookie host-only: no `Domain` attribute, so the browser sends it only to the host that set
it and the public site's requests stay cookie-free. Source: https://www.rfc-editor.org/rfc/rfc6265#section-5.3
(host-only flag when no Domain attribute is given; verified 2026-10-31).

## The route-inventory allowlist

The product app's inventory test lists every route reachable without authentication. Each allowlist entry
carries a one-line reason:

```text
login                  auth entry point
password reset         auth recovery
invitation accept      links from invitation mail
webhooks/*             signed provider callbacks
api/*                  token-authenticated public API
```

A new unauthenticated route fails the test until someone adds it with a reason. A marketing page cannot land in
the app by accident.

## Choosing a framework other than Nuxt

The split itself has no exception. The framework is a default: a project that builds its public site with a
static site generator or another meta-framework writes an ADR that names the trade-off (a second frontend
stack to maintain, or fewer rendering modes per route) and keeps every other rule in this skill.
