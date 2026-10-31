# Guard artifacts

## Contents

- 1. Route inventory (product app)
- 2. Cache decision and header check (public site)
- 3. Inertia SSR config test
- 4. ESLint rules
- 5. Sanitizer and the v-html guard
- 6. CSP header check
- 7. i18n tests and the removed-key check
- 8. Typecheck in the release workflow
- 9. Prop-casing guard
- 10. Lint on a clean checkout

Each guard enforces one rule of the skill. Add the guard with the change it protects and see it fail once
before trusting it. Paths and names are examples; adapt them to the project.

## 1. Route inventory (product app)

Fails when a route reachable without authentication is missing from the allowlist.

```php
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Str;

it('exposes only allowlisted routes without authentication', function () {
    $allow = [
        'login' => 'auth entry point',
        'password.*' => 'auth recovery',
        'invitations.accept' => 'links from invitation mail',
        'webhooks.*' => 'signed provider callbacks',
    ];

    $open = collect(Route::getRoutes()->getRoutes())
        ->reject(fn ($route) => collect($route->gatherMiddleware())
            ->contains(fn ($m) => is_string($m) && Str::startsWith($m, 'auth')))
        ->map(fn ($route) => $route->getName() ?? $route->uri())
        ->reject(fn ($name) => collect(array_keys($allow))->contains(fn ($pattern) => Str::is($pattern, $name)))
        ->values()
        ->all();

    expect($open)->toBe([]);
});
```

Framework and package routes without auth (health check, CSRF cookie, storage links) also go on the allowlist,
each with a reason. Token-authenticated API routes count as authenticated when their middleware starts with
`auth`.

## 2. Cache decision and header check (public site)

A pure function with a unit table, plus a CI request against the built preview. The function sketch, the table
rows and the curl check are in the rendering and caching reference of this skill.

## 3. Inertia SSR config test

One assertion that `inertia.ssr.enabled` is false, plus a build check that no SSR entry exists for the
dashboard bundle. Sketch in the Inertia dashboard reference.

## 4. ESLint rules

```js
// eslint.config.js (excerpt)
{
  rules: {
    'vue/no-v-html': 'error',
    'no-restricted-imports': ['error', {
      paths: [
        { name: 'example-tracking-sdk', message: 'Calls a third-party host from the browser. Route it through the backend or drop it.' },
      ],
    }],
    // plus 'no-restricted-syntax' against string app URLs, see the typed contracts reference
  },
}
```

Rule name verified at https://eslint.vuejs.org/rules/no-v-html.html (2026-10-31).

## 5. Sanitizer and the v-html guard

- Unit tests for the sanitizer with the payload list from the XSS reference.
- A guard that every file using `v-html` also uses the sanitizer:

```sh
#!/bin/sh
set -eu
bad=$(grep -rlE --include='*.vue' 'v-html=' resources/js 2>/dev/null | while IFS= read -r f; do
  grep -q 'safeHtml' "$f" || echo "$f"
done)
[ -z "$bad" ] || { echo "v-html without safeHtml:"; echo "$bad"; exit 1; }
```

## 6. CSP header check

Runs against the built preview. `ERROR_PATH` is a route that answers 500 in preview builds only.

```sh
#!/bin/sh
set -eu
base="${PREVIEW_URL:?set PREVIEW_URL}"
for path in / /does-not-exist "${ERROR_PATH:-}"; do
  [ -n "$path" ] || continue
  csp=$(curl -s -o /dev/null -D - "$base$path" | tr -d '\r' | grep -i '^content-security-policy:' || true)
  [ -n "$csp" ] || { echo "no CSP on $path"; exit 1; }
  script=$(printf '%s' "$csp" | sed -n 's/.*script-src\([^;]*\).*/\1/p')
  printf '%s' "$script" | grep -qE "'nonce-|'sha(256|384|512)-" \
    || { echo "script-src without nonce or hash on $path"; exit 1; }
done
echo "csp ok"
```

A missing `script-src` fails too, on purpose: a policy that falls back to `default-src` for scripts is not
checked here. Pair it with the browser test for `securitypolicyviolation` events from the CSP reference.

## 7. i18n tests and the removed-key check

- Syntax, parity and usage tests as described in the i18n reference.
- Removed-key check against the previous release tag:

```sh
#!/bin/sh
set -eu
prev="${PREV_TAG:?set PREV_TAG}"; file="${LOCALE_FILE:-resources/js/locales/en.json}"
old=$(mktemp)
git show "$prev:$file" > "$old"
python3 - "$old" "$file" "${REMOVAL_LIST:-resources/js/locales/_remove_after.txt}" <<'PY'
import json, sys
def keys(d, p=""):
    for k, v in d.items():
        yield from keys(v, p + k + ".") if isinstance(v, dict) else [p + k]
old, new = (set(keys(json.load(open(f)))) for f in sys.argv[1:3])
try:
    allowed = {l.strip() for l in open(sys.argv[3]) if l.strip()}
except FileNotFoundError:
    allowed = set()
gone = sorted(old - new - allowed)
if gone:
    print("removed without a removal entry:", *gone, sep="\n  ")
    sys.exit(1)
PY
rm -f "$old"
```

## 8. Typecheck in the release workflow

`vue-tsc --noEmit` or `nuxi typecheck` as a step of the workflow that builds the release artifact, so a type
error blocks the release and not only an advisory job.

## 9. Prop-casing guard

The grep guard for snake_case prop declarations in the typed contracts reference, plus one browser assertion
per critical component that the attribute form of a prop is absent.

## 10. Lint on a clean checkout

The first lint step in CI runs before route or type generation, on a fresh checkout, with generated directories
in the ignore list. Lint results on a clean checkout and on a tree with generated files must be identical.
