# Typed contracts

Routes, page props and component props are contracts between server and client. Make each one fail at
typecheck or in a test, not at runtime.

## Route helpers

- Build URLs with generated helpers: Wayfinder for Laravel (https://github.com/laravel/wayfinder, beta before
  1.0, verified 2026-10-31), the framework's typed routes elsewhere. Check the generator's API for the installed
  version before writing calls; it changes before 1.0.
- Inject the tenant parameter in one place (the generator's URL-defaults hook, or one wrapper around it), not
  by hand at each call site.
- Generated directories are gitignored, and excluded from ESLint and the formatter. Wayfinder writes to
  `resources/js/wayfinder`, `resources/js/actions` and `resources/js/routes` by default, and its README says
  they may be gitignored because every build regenerates them.
- CI lints a clean checkout before any generation step, so local generated files cannot hide or create
  findings.

ESLint guard against string app URLs (adapt the selectors to your call sites):

```js
// eslint.config.js (excerpt)
{
  rules: {
    'no-restricted-syntax': ['error',
      { selector: "CallExpression[callee.name='fetch'] > Literal[value=/^\\//]", message: 'Use a generated route helper.' },
      { selector: "CallExpression[callee.property.name='visit'] > Literal[value=/^\\//]", message: 'Use a generated route helper.' },
      { selector: "CallExpression[callee.name='fetch'] > TemplateLiteral[quasis.0.value.raw=/^\\//]", message: 'Use a generated route helper.' },
    ],
  },
}
```

For `href` bindings in templates, add the equivalent check in the Vue template lint or a grep guard for
`:href="'/` and ``:href="`/``.

## Page props

Pick one and enforce it:

1. Generate TypeScript types from backend DTOs or resources in the build, and import them in pages.
2. A contract test: a feature test renders the page, takes the real prop payload, and compares its keys and
   types with a schema that the frontend type is also generated from.

Hand-written types without either drift silently.

## Component props

- `defineProps<T>()` with a TypeScript interface.
- Declare props in camelCase and bind them in kebab-case. Vue's convention, see
  https://vuejs.org/guide/components/props.html (verified 2026-10-31).
- A binding that matches no declared prop becomes a fallthrough attribute on the root element. A
  snake_case declaration (`line_items`) bound as `:line-items` is camelized to `lineItems`, matches nothing,
  and renders as a literal DOM attribute, often `[object Object]`.
- Never reuse a snake_case wire-payload interface as a props type. Map it to a camelCase props type at the page
  boundary.

Guard test for snake_case prop declarations:

```sh
#!/bin/sh
set -eu
# Fails when a defineProps type declares a snake_case member.
hits=$(grep -rnE --include='*.vue' '^[[:space:]]+[a-z]+(_[a-z0-9]+)+[?]?[[:space:]]*:' resources/js app 2>/dev/null || true)
[ -z "$hits" ] || { echo "$hits"; echo "snake_case prop declarations found"; exit 1; }
```

Adjust the directories to your layout. The pattern also matches object literals in `.vue` files; narrow it to
`defineProps` blocks if it reports false positives.

## Typecheck gate

`vue-tsc --noEmit` (or `nuxi typecheck`) runs in the workflow that builds the release artifact and blocks it.
An advisory job in a separate workflow does not count.

## Proof in the browser

For each critical component, one browser assertion checks that the attribute form of a prop is absent from the
rendered HTML (for example no `line-items=` attribute). Server-side page tests cannot see this; see
`browser-verification`.
