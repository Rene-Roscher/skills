---
name: web-architecture
description: "Decides where web surfaces live and how they render, and sets the frontend safety rules that follow: public marketing, pricing, docs and company pages in their own deployment and failure domain (Nuxt by default) with prerendering and CDN caching; authenticated dashboards as client-rendered Inertia and Vue pages without SSR; no shared caching of authenticated output; generated typed routes instead of string URLs; typed page props; vue-i18n messages that compile, match across locales and resolve; a CSP without script 'unsafe-inline'; and v-html only on sanitized content. Use when planning a landing, pricing or docs site, choosing SSR, CSR or prerendering, editing nuxt.config routeRules, Inertia SSR settings, security headers or locale JSON files, or reviewing .vue files that use v-html or hardcoded URLs. Not for visual design or styling, browser test mechanics (browser-verification), or backend layering (laravel-architecture)."
license: Apache-2.0
compatibility: "Vue 3, Inertia 2 or later, Nuxt 3 or 4, vue-i18n 9 or later. Config syntax comes from the vendor docs for the installed versions."
metadata:
  author: "Rene Roscher"
paths:
  - "**/*.vue"
  - "**/resources/js/**"
  - "**/nuxt.config.*"
  - "**/app.config.*"
  - "**/config/inertia.php"
  - "**/locales/**/*.json"
  - "**/i18n/**/*.json"
  - "**/vite.config.*"
---

# Web architecture

This skill decides which web surface lives where and how it renders: public pages as their own deployment,
dashboards behind login as client-rendered pages. It then sets the frontend safety rules that follow from that
split: caching, CSP, `v-html`, i18n message syntax, typed routes and props. Config syntax (Nuxt `routeRules`,
Inertia settings, CSP modules, Wayfinder) stays in the vendor docs linked under Sources. The failure it
prevents: the website going down with the product, and frontend bugs that every server-side test passes.

## Applies when / does not apply

- Applies: planning a landing, pricing, docs, company or legal page; choosing prerendering, ISR/SWR, SSR or
  client rendering; writing cache headers or route rules; setting Inertia SSR; writing security headers;
  editing locale JSON; building URLs or page-prop types in frontend code; reviewing `.vue` files with `v-html`,
  string URLs or permission checks.
- Does not apply: visual design and styling, copywriting, browser test mechanics (`browser-verification`),
  backend layering (`laravel-architecture`), edge proxies and TLS, performance budgets, translating strings,
  general Vue questions that the Vue docs answer.
- Out of scope here: public status pages or embeds that show live product data. They need their own cache and
  failure rules and are a separate decision.

## Rules

- [invariant] Public pages (marketing, product, pricing, docs, company, legal) never run inside the product's
  backend app or deployment: they have their own build, deploy target and runtime, and need nothing from the
  product at request time. Build-time data fetches with a fallback are fine. Why: the product runtime gets
  frozen or taken down for reasons unrelated to the site (an emergency runtime patch, a migration, an
  incident), and a shared runtime takes the site down exactly when prospects and customers look for
  information. Test: a route-inventory test in the product app lists every route reachable without
  authentication and fails on any route missing from a reasoned allowlist (login, password reset, invitation
  accept, webhooks, public API); the public site has its own CI workflow and deploy target.

- [invariant] `v-html` renders only sanitized or fully trusted content. Never bind user-, customer- or
  third-party-controlled data to it, including a translated string that interpolates such data. Rich text goes
  through one shared sanitizer composable (DOMPurify or equivalent) with an explicit tag and attribute
  allowlist; confirmation dialogs take plain text plus substrings to emphasize, never HTML. Why: an i18n string
  that interpolates an entity name into `v-html` is an XSS sink even when the translation is trusted. Test:
  ESLint `vue/no-v-html` set to error, each remaining use carries a disable comment that names the sanitizer;
  sanitizer unit tests with `<img src=x onerror=...>`, `javascript:` URLs and SVG `onload` payloads come back
  inert. Source: https://vuejs.org/api/built-in-directives.html#v-html and
  https://eslint.vuejs.org/rules/no-v-html.html (verified 2026-10-31).

- [invariant] The effective script policy authorizes scripts only by nonce or hash: a CSP on every response,
  error responses included, set in one response hook; a fresh nonce per response for server-rendered HTML,
  hashes for prerendered or cached HTML, `'strict-dynamic'` where the framework loads chunks at runtime, plus
  `object-src 'none'`, `base-uri`, `frame-ancestors` and `form-action`. `'unsafe-inline'` may sit in
  `script-src` only next to a nonce or hash, where CSP Level 3 browsers ignore it. `style-src 'unsafe-inline'`
  is tolerated when the framework injects styles at runtime; then restrict `img-src`. Why: without it every
  injection sink becomes script execution, and a nonce inside cached HTML is a reused nonce. Test: a CI step
  against the built preview asserts the header on a 200, a 404 and a 500, that `script-src` contains
  `'nonce-` or `'sha`, and that `'unsafe-inline'` never appears without one of them; a browser test records
  zero `securitypolicyviolation` events on key pages. Source: https://www.w3.org/TR/CSP3/ (the inline-behavior
  algorithm and "Nonce Reuse") and https://nuxt-security.vercel.app/headers/csp (verified 2026-10-31).

- [invariant] Authenticated or personalized responses never enter a shared cache. The cache decision lives in
  one pure function that defaults to `private, no-store` and never caches errors or per-visitor redirects;
  a cacheable response carries no `Set-Cookie`. Why: a shared cache that stores one user's page serves it to
  the next visitor, and a cached 404 or 503 shadows the last good page. Test: a unit table of route class,
  status and auth state against the expected header; a CI request against the built preview checks an
  authenticated page for `private` or `no-store` and a cacheable page for the absence of `Set-Cookie`.

- [invariant] Client-side permission checks are presentation only; every action is authorized on the server.
  Why: anyone can call the endpoint directly or read the page props. Test: an authorization test per action
  that calls the server as a user without the permission and expects a denial; review rejects a change whose
  only enforcement is a hidden button. Ownership of the server rules sits with `authorization-rbac`.

- [invariant] vue-i18n messages compile, match across locales and resolve. `{`, `}`, `@`, `$` and `|` are
  message syntax: write literal characters as literal interpolation (`{'@'}`) and keep code or JSON examples
  out of locale files. Why: one unescaped `@` crashed a dialog only in the production build, one `{` made a
  whole locale file fail while the page still returned 200, and a key missing from every locale shipped as a
  raw dotted key. Test: three blocking CI tests, each seen red once: a syntax test that compiles every message
  of every locale file, a parity test (same key set in all locales, no blank leaves), and a usage test (every
  static `t()`, `te()` and `<i18n-t keypath>` key resolves in every locale; dynamic key patterns sit on an
  allowlist whose source needle must still exist). Source:
  https://vue-i18n.intlify.dev/guide/essentials/syntax (verified 2026-10-31).

- [default] The public site is a Nuxt project. Trade-off: Nuxt ties the site to Vue and a Node build;
  a static site generator or another meta-framework suits a content-only site as well. Deviate only with an
  ADR that names this trade-off. Source: https://nuxt.com/docs/4.x/guide/concepts/rendering (verified
  2026-10-31).

- [default] Choose the rendering mode per route class: prerender static pages, ISR or SWR for content that
  changes on a schedule, server rendering only where a page is personalized. Public pages get `s-maxage` plus
  `stale-while-revalidate` (and `stale-if-error` where availability matters), vary on encoding only, and
  carry the locale in the URL instead of a cookie. Trade-off: content changes wait for a rebuild or a
  revalidation window. Deviate only with an ADR that names this trade-off. Source:
  https://nuxt.com/docs/4.x/guide/concepts/rendering (`routeRules`, verified 2026-10-31).

- [default] Dashboards behind login are client-rendered Inertia pages: SSR off explicitly in the Inertia
  config, no SSR bundle built, no SSR process run. Enable SSR only for a public Inertia page that must be
  indexed, and then run, health-check and monitor the SSR server. Trade-off: first paint waits for the
  JavaScript bundle. Deviate only with an ADR that names this trade-off. Proof: a config test asserts the SSR
  flag; the build has no SSR entry for the dashboard. Source: https://inertiajs.com/server-side-rendering
  (SSR is for indexing, runs a Node process, and falls back to client rendering when it fails; verified
  2026-10-31).

- [default] Frontend code builds URLs with generated, typed route helpers (Wayfinder for Laravel), with tenant
  defaults injected centrally. Generated directories are gitignored and excluded from lint and format.
  Trade-off: a generation step in dev, build and CI. Deviate only with an ADR that names this trade-off. Proof: an
  ESLint rule rejects string literals starting with `/` in `fetch`, router visits and `href` bindings; CI
  lints a clean checkout before generation. Source: https://github.com/laravel/wayfinder (beta before 1.0,
  generated directories may be gitignored; verified 2026-10-31).

- [default] Page props are typed from the backend contract: generated from DTOs or resources, or pinned by a
  contract test against real responses. Components use `defineProps<T>()`, declare props in camelCase and
  bind them in kebab-case, and never reuse a snake_case wire-payload type as props. Trade-off: generation or
  contract tests cost build time and couple frontend names to the backend. Deviate only with an ADR that names
  this trade-off. Proof: `vue-tsc` or `nuxi typecheck` blocking in the workflow that builds the release; a
  guard test for snake_case prop declarations. Source: https://vuejs.org/guide/components/props.html (prop
  name casing; verified 2026-10-31).

- [default] Survive deploy skew: renamed or removed i18n keys and other runtime-fetched resources stay for one
  release, and a stale-chunk error after a deploy triggers one guarded hard reload. Trade-off: dead keys and
  assets live one release longer. Deviate only with an ADR that names this trade-off. Proof: a CI diff of
  removed locale keys against the previous release tag; a unit test for the reload guard. Source:
  https://vite.dev/guide/build#load-error-handling (`vite:preloadError`; verified 2026-10-31).

- [default] Locale is explicit and server-driven: public pages carry it in the path with `html lang` and
  `hreflang` per locale, only the bare root redirects per visitor (`no-store`); the dashboard takes the
  server's locale and keeps `document.documentElement.lang` in sync. Dates, numbers and money go through
  `Intl`. Trade-off: longer URLs and one redirect on the root. Deviate only with an ADR that names this
  trade-off. Source: https://i18n.nuxtjs.org/docs/guide and
  https://i18n.nuxtjs.org/docs/guide/browser-language-detection (verified 2026-10-31).

- [default] Shared client state is tenant-scoped and SSR-safe: module-level caches drop the previous
  tenant's data when the tenant changes, start no timers during SSR, and realtime subscriptions in persistent
  layouts resubscribe on tenant switch. Trade-off: an empty state shows briefly after a switch. Deviate only
  with an ADR that names this trade-off. Proof: a unit test switches tenant and asserts the cache is empty
  before the new fetch resolves.

## Procedure

1. Classify the surface: public and indexable, authenticated dashboard, or live-data status page or embed
   (out of scope here). A public page goes to the separate site; a dashboard page goes to Inertia without SSR.
2. Read the installed versions from the lockfiles before writing config. Check route rules, CSP module, i18n
   module and Inertia options against the vendor docs for those versions (a documentation index tool such as
   Context7, or the installed package source). If neither is available, say the option is unverified
   (`evidence-before-claims`).
3. For public routes, write the route-class table: rendering mode, cache header, cookie policy. Implement the
   cache decision as one pure function with its unit table.
4. Set the CSP in one response hook: nonce for server-rendered responses, hashes for prerendered and cached
   pages, a separate looser policy for the dev server.
5. For each rule the change touches, add or update its guard from
   [references/guard-artifacts.md](references/guard-artifacts.md) and see it fail once.
6. Prove rendered behaviour (headers, CSP violations, props reaching components, `lang`) with
   `browser-verification`.

## Traps

- An emergency runtime patch can keep the product runtime down for hours, for example while patched base
  images lag behind the release. A website in that runtime is down for the same hours. Detect: the
  route-inventory test lists marketing routes.
- One `Set-Cookie` on public responses (session or locale) made every response uncacheable, and the edge cache
  was off without any error. Detect: request a public page from the built preview and look for `Set-Cookie`.
- An i18n module's browser-language detection sets a cookie by default. Keep it on the uncacheable root
  redirect only, or turn detection off.
- A cached error page shadowed the last good page until the TTL ran out. Detect: the cache function's unit
  table has rows for 404, 500 and 503.
- A half-enabled Inertia SSR setup fails quietly and falls back to client rendering, so every page view pays
  for a failed SSR request. Detect: the config test, and SSR server logs when SSR is meant to be on.
- A component declared `line_items` while the template bound `:line-items`; the value rendered as a literal
  DOM attribute while the server-side page test stayed green.
- Generated route files existed only locally: lint was green locally and red in CI with hundreds of errors.
- Right after a deploy, cached old HTML loaded new message files and showed raw keys for a short window.

## Done when

- The surface is classified, public pages live outside the product deployment, and the route-inventory test is
  green.
- Every cache header comes from the decision function, and authenticated output is `private` or `no-store`.
- The CSP check passes on 200, 404 and 500 responses of the built preview, with zero violations in the browser.
- No unsanitized `v-html`; the three i18n tests are green; typecheck blocks the release build.
- Each guard the change touches has been seen red once, and the rendered result was checked with
  `browser-verification`.

## References

- [references/surface-split.md](references/surface-split.md): load when planning a landing, docs, pricing or
  company page, or when arguing the split in review.
- [references/rendering-and-caching.md](references/rendering-and-caching.md): load when choosing prerender,
  ISR, SWR, SSR or client rendering, or writing route rules and cache headers.
- [references/csp.md](references/csp.md): load when writing or reviewing security headers, nonces or hashes,
  the dev policy, or the Vite nonce in Laravel.
- [references/xss-sinks.md](references/xss-sinks.md): load for any `v-html`, `innerHTML`, markdown rendering,
  style binding from data, or confirmation dialog.
- [references/i18n-safety.md](references/i18n-safety.md): load when editing locale JSON, adding, renaming or
  removing keys, using dynamic keys, or setting up locale routing.
- [references/typed-contracts.md](references/typed-contracts.md): load when working on route helpers,
  page-prop types, prop casing or typecheck gates.
- [references/inertia-dashboard.md](references/inertia-dashboard.md): load for Inertia specifics: SSR off,
  partial reloads, polling, realtime-triggered reloads, the fetch wrapper.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the tests and lint rules
  that enforce these rules.

## Sources

- https://nuxt.com/docs/4.x/guide/concepts/rendering: hybrid rendering with `routeRules` (`prerender`, `swr`,
  `isr`, `ssr: false`), verified 2026-10-31.
- https://inertiajs.com/server-side-rendering: SSR serves indexable HTML, runs a Node background process, falls
  back to client rendering on failure; `config/inertia.php` `ssr.enabled`; verified 2026-10-31 (v3 docs).
- https://vuejs.org/api/built-in-directives.html#v-html: "Only use v-html on trusted content and never on
  user-provided content", verified 2026-10-31.
- https://eslint.vuejs.org/rules/no-v-html.html: rule `vue/no-v-html`, in the recommended preset, verified
  2026-10-31.
- https://www.w3.org/TR/CSP3/: a nonce or hash source means a source list does not allow all inline script
  ("Does a source list allow all inline behavior for type?"); the server generates a unique nonce each time it
  transmits a policy ("Nonce Reuse"); verified 2026-10-31.
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src:
  `'strict-dynamic'` propagates trust and ignores allowlists and `'unsafe-inline'`; nonce unique per request;
  verified 2026-10-31.
- https://nuxt-security.vercel.app/headers/csp: nonce for SSR only, hashes for SSG only, `ssg.hashScripts`,
  `style-src 'unsafe-inline'` as the default for Nuxt apps, verified 2026-10-31.
- https://laravel.com/docs/12.x/vite#content-security-policy-csp-nonce: `Vite::useCspNonce()` adds the nonce to
  generated script and style tags, verified 2026-10-31.
- https://vue-i18n.intlify.dev/guide/essentials/syntax: special characters and literal interpolation, verified
  2026-10-31.
- https://vue-i18n.intlify.dev/guide/migration/breaking: from v9 the compiler treats `{`, `}`, `@`, `$` and `|` as
  syntax, so literal use needs literal interpolation, verified 2026-10-31.
- https://i18n.nuxtjs.org/docs/guide: routing strategies; browser detection cookie and `redirectOn: 'root'`
  documented for v10.6, verified 2026-10-31.
- https://github.com/laravel/wayfinder: generated route and action helpers, beta before 1.0, verified
  2026-10-31.
- https://vuejs.org/guide/components/props.html: camelCase declaration, kebab-case binding, undeclared
  attributes fall through, verified 2026-10-31.
- https://vite.dev/guide/build#load-error-handling: `vite:preloadError` on failed dynamic imports after a
  deploy, verified 2026-10-31.
