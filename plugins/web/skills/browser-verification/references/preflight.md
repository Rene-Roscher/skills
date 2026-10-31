# Preflight

Run before the first browser run in a session, and again whenever a result contradicts the source. Paste the
output into the report.

## The four checks

1. Target: the browser loads the built bundle, or the report says it ran against a dev server.
2. Served change: the page or asset the server sends contains the change.
3. Mock fallback: no dev-only fallback to hardcoded or mock data is active.
4. Overlay: no dev-server error overlay is on the page.

## Checks

```sh
#!/bin/sh
# ui-preflight.sh: copy into the project and adapt the paths and markers.
set -eu
url="${APP_URL:?set APP_URL}"; page="${PAGE:-/}"; needle="${NEEDLE:?set NEEDLE to a string the change adds}"

echo "preflight $(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ -f public/hot ]; then echo "  target:     dev server (public/hot present)"; else echo "  target:     built assets"; fi
[ -f public/build/manifest.json ] && echo "  manifest:   $(ls -l public/build/manifest.json)"

html=$(curl -fsS "$url$page")
count=$(printf '%s' "$html" | grep -c -- "$needle" || true)
echo "  served:     $page contains '$needle' $count time(s)"
printf '%s' "$html" | grep -q 'vite-error-overlay' && echo "  overlay:    PRESENT" || echo "  overlay:    none in served HTML"
[ "$count" -gt 0 ] || { echo "  result:     the served page does not contain the change"; exit 1; }
```

When the change lives in a JavaScript chunk rather than in the HTML, find the chunk the page references and
grep that file instead. For SSR pages behind ISR, SWR or a CDN, the served HTML can be older than the build:
compare the build ID or the `age` header before judging CSS or markup.

The mock-fallback check is project-specific. List the dev-host fallbacks (mock APIs, fixture switches,
hardcoded sample data) in the project facts and check each one here.

## Dev-server marker

Laravel's Vite integration loads the dev server whenever the hot file exists; by default that is `public/hot`
(`Illuminate\Foundation\Vite`, framework 12.x source, verified 2026-10-31). A headless browser in a test
process usually cannot reach the HMR host, so the app never mounts and tests time out on a blank page. Skip
instead, with a message that says what to do:

```php
// tests/Browser/Pest.php or the shared browser setup
beforeEach(function () {
    if (file_exists(public_path('hot'))) {
        $this->markTestSkipped('Vite dev server marker public/hot present: stop the dev server or run the production build.');
    }
});
```

```ts
// playwright global setup
import { existsSync } from 'node:fs'
export default async function globalSetup() {
  if (existsSync('public/hot')) throw new Error('Vite dev server marker public/hot present: run the production build first.')
}
```

## Error overlay before the first interaction

The Vite dev overlay is the custom element `vite-error-overlay` (checked in Vite 7.3.1's client, 2026-10-31).
When a run must use a dev server, assert it is absent before the first click:

```ts
await expect(page.locator('vite-error-overlay')).toHaveCount(0)
```

An overlay means the build is broken. Fix the build, rerun the generator if one is involved, then rerun the
test. Do not change the test.

## Example output

```text
preflight 2026-10-31T14:02:11Z
  target:     built assets
  manifest:   -rw-r--r-- 1 ci ci 2310 Oct 31 14:01 public/build/manifest.json
  served:     /invoices contains 'data-testid="invoice-total"' 1 time(s)
  overlay:    none in served HTML
```
