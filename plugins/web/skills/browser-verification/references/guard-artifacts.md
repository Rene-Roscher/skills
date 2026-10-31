# Guard artifacts

## Contents

- 1. Shared setup with absence-of-failure checks
- 2. Guard over browser test files
- 3. Measurement helpers
- 4. Preflight script
- 5. CI job
- 6. Optional visual baselines
- 7. Write-up template

Each guard enforces one rule of the skill. Add it with the first browser test of a project and see it fail
once. Paths are examples.

## 1. Shared setup with absence-of-failure checks

Playwright Test: an automatic fixture that every test gets without asking for it.

```ts
// tests/e2e/fixtures.ts
import { test as base, expect } from '@playwright/test'

export const test = base.extend<{ failures: void }>({
  failures: [async ({ page, baseURL }, use) => {
    const problems: string[] = []
    const own = (url: string) => !!baseURL && url.startsWith(baseURL)
    page.on('pageerror', (e) => problems.push(`js error: ${e.message}`))
    page.on('requestfailed', (r) => { if (own(r.url())) problems.push(`request failed: ${r.method()} ${r.url()}`) })
    page.on('response', (r) => { if (own(r.url()) && r.status() >= 500) problems.push(`HTTP ${r.status()} ${r.url()}`) })
    await page.addInitScript(() => {
      (window as any).__csp = []
      document.addEventListener('securitypolicyviolation', (e) => (window as any).__csp.push(e.violatedDirective))
    })
    await use()
    const csp: string[] = await page.evaluate(() => (window as any).__csp ?? []).catch(() => [])
    expect([...problems, ...csp.map((d) => `csp violation: ${d}`)]).toEqual([])
  }, { auto: true }],
})
export { expect }
```

Tests import `test` and `expect` from this file instead of `@playwright/test`. Expected 4xx responses (a 422 on
a validation test) are asserted in the test itself; 5xx and failed requests to your own origin always fail.

Pest browser plugin: end every test through one helper that calls `assertNoJavaScriptErrors()` (and
`assertNoConsoleLogs()` where the app logs nothing in production), so no test can forget it.

## 2. Guard over browser test files

```sh
#!/bin/sh
# Fails on fixed waits, headed mode, text selectors on copy and attached user browsers.
set -eu
dirs="${BROWSER_TEST_DIRS:-tests/Browser tests/e2e e2e}"
pattern='waitForTimeout\(|(^|[^A-Za-z_])u?sleep\(|->wait\([0-9]|headless:[[:space:]]*false|--headed|headed\(\)|has-text\(|["'"'"']text=|launchPersistentContext\(|connectOverCDP\(|--user-data-dir'
set --
for d in $dirs; do [ -d "$d" ] && set -- "$@" "$d"; done
for f in playwright.config.*; do [ -f "$f" ] && set -- "$@" "$f"; done
[ "$#" -gt 0 ] || { echo "no browser test files found"; exit 0; }
hits=$(grep -rnE "$pattern" "$@" | grep -v '/debug/' || true)
[ -z "$hits" ] || { echo "$hits"; echo "forbidden pattern in browser tests"; exit 1; }
echo "browser test guard ok"
```

Helpers under a `debug/` directory are exempt, for local debugging only.

## 3. Measurement helpers

- The collector from the measurement reference, versioned in the project (for example
  `tests/Browser/Support/measure.js`).
- `measure-check.py` from this skill, run on every measurement JSON the suite writes. Copy it into the project
  if CI must run without the skill installed.
- CI runs `measure-check.py self-test`, and a unit test feeds the project's own contrast helper (if any) the
  same colour pairs and compares with `measure-check.py contrast`.

## 4. Preflight script

`ui-preflight.sh` from the preflight reference, plus the dev-server skip in the shared setup.

## 5. CI job

```yaml
browser-tests:
  runs-on: ubuntu-latest
  timeout-minutes: 30
  permissions:
    contents: read
  steps:
    - uses: actions/checkout@[pinned commit]
    - uses: actions/setup-node@[pinned commit]
      with:
        node-version-file: .nvmrc
    - run: npm ci
    - run: npm run build
    - run: npx playwright install --with-deps chromium
    - run: npx playwright test
    - run: python3 tools/measure-check.py check tests/Browser/artifacts/measure-chromium.json
    - if: always()
      uses: actions/upload-artifact@[pinned commit]
      with:
        name: browser-artifacts
        path: tests/Browser/artifacts/
        retention-days: 14
```

Pin the actions the way the project pins all actions (see `github-actions-hardening`). Build the assets before
the run; never run the suite against a dev server in CI.

## 6. Optional visual baselines

Baselines (`expect(locator).toHaveScreenshot()` in Playwright, `assertScreenshotMatches()` in the Pest plugin)
suit stable components only. Generate and update them on the CI image, since fonts and rendering differ
between machines. Review the diff images in the pull request before updating, and never update a baseline to
turn a red test green without looking at the difference.

## 7. Write-up template

The template in the evidence-format reference, copied to `docs/verification-report.md` in the project if the
team wants one shared file.
