---
name: browser-verification
description: "Proves UI changes in a real headless browser before anything is reported as done: a preflight that checks the served build instead of the source tree, deterministic waits instead of sleeps, data-testid selectors for copy-driven elements, element screenshots as evidence, overflow, contrast, target size and fit measured as numbers against thresholds, no JavaScript errors, failed requests or CSP violations, exact request and toast counts, and isolated seeded fixtures. Use when asked to verify, screenshot or visually check a page, confirm a frontend fix works, check contrast, overflow, dark mode or responsive layout, write tests/Browser or *.spec.ts files, or before reporting any UI task as finished. Not for unit or feature tests that need no browser, for designing the UI, for performance or load testing, or for driving the user's own browser or logged-in accounts."
license: Apache-2.0
compatibility: "Playwright Test 1.61 or later, or the Pest 4 browser plugin. Python 3 for the bundled measurement checker. Any server-rendered or single-page frontend."
metadata:
  author: "Rene Roscher"
paths:
  - "**/tests/Browser/**"
  - "**/tests/e2e/**"
  - "**/e2e/**"
  - "**/*.spec.ts"
  - "**/*.e2e.ts"
  - "**/playwright.config.*"
---

# Browser verification

A UI claim without a browser run is unverified. This skill decides how an agent proves a UI change in a real
headless browser and what counts as evidence: measured numbers and element screenshots, never "looks fine".
Runner syntax stays in the Playwright and Pest docs linked under Sources. The failure it prevents: a fix
reported as done that never changed what the user sees.

## Applies when / does not apply

- Applies: verifying, screenshotting or visually checking a page; confirming a frontend fix; contrast,
  overflow, fit, dark mode or responsive checks; writing or fixing browser tests (`tests/Browser`, `*.spec.ts`);
  any UI task about to be reported as finished.
- Does not apply: unit or feature tests that need no browser, typecheck errors, UI design, performance budgets
  or load tests, scraping other sites, and anything in the user's own browser, mail or logged-in accounts.
- Where things render and why (SSR, CSP, i18n rules) is decided in `web-architecture`.

## Rules

- [invariant] Report only what was seen working. A UI item is done only with browser evidence: the command,
  the result, the artifact path. Otherwise it is reported as "implemented, not verified in a browser", with
  the reason and what was checked instead (source read, unit test, server-side page test). Why: items
  reported as fixed did not change the user-visible symptom. Test: every UI item in the report carries a
  command, a result and an artifact path that exists, or the words "not verified in a browser". Status
  vocabulary follows `verify-before-done`.

- [invariant] Never use the user's browser, profile, cookies or accounts. Launch a fresh browser with a fresh
  context; never attach to a running browser, never point at a real profile directory, never import cookies.
  Why: a real profile mixes the user's sessions into the test and can act on their accounts. Test: a guard
  over test files and CI config fails on `launchPersistentContext(`, `connectOverCDP(` and `--user-data-dir`
  outside an allowlisted CI fixture.

- [default] Run every browser headless. Headed mode is a local debugging choice the user makes, not something
  the agent switches on. Trade-off: headless rendering differs from a user's browser in a few known places,
  which the report lists as not verifiable headless. Deviate only with an ADR that names this trade-off.
  Proof: the same guard fails on `headless: false`, `--headed` and `headed()` in committed files. Source:
  https://playwright.dev/docs/debug ("Playwright runs browsers in headless mode by default", verified
  2026-10-31).

- [invariant] Verify what is served, not what is in the source tree. Before the first assertion, run the
  preflight and paste its output into the report: built bundle or dev server, the served artifact contains
  the change, no dev-host mock fallback, no dev-server error overlay. Browser tests run against built assets
  and skip with an actionable message when a dev-server marker is present (Laravel's Vite hot file, by
  default `public/hot`). Why: a stale SSR cache served old markup, dev fixtures sent plain strings where
  production sends objects, and an unreachable HMR host left the app unmounted. Test: the preflight greps
  the served page or asset for the new string or class and fails when it is absent; the shared setup skips
  when the hot file exists.

- [invariant] Fixtures are isolated, seeded and side-effect free. Each test creates its own tenant and user
  through the application's real creation path, passes every gate a real user passes (terms, onboarding,
  welcome dialogs), reuses the session as stored state, and cleans up. Never a shared development database
  with ad-hoc users, never production data, never a code path that notifies real people. Why: gate dialogs
  dimmed the page and falsified every colour measurement, and logins landed on consent pages. Test: one shared
  fixture helper used by every browser test; a test asserts that the mail, SMS, chat and webhook transports
  of the test environment are fakes. See `safe-actions`.

- [invariant] Every browser test asserts the absence of failure: no JavaScript errors, no failed requests to
  your own origin, zero CSP violations, exact counts where counts matter (one toast, one POST per submit), and
  no known failure signature (the fallback sentence shown when data did not arrive, a prop rendered as a DOM
  attribute). Why: a double submit sent two POSTs while the positive assertions passed. Test: a shared
  after-each helper runs the error, network and CSP checks; a request counter records requests per action.
  Source: https://pestphp.com/docs/browser-testing (`assertNoJavaScriptErrors`, `assertNoConsoleLogs`;
  verified 2026-10-31).

- [invariant] Wait for the condition you are about to assert, then read or count. No fixed timeouts as
  synchronization (`waitForTimeout`, `sleep`, `usleep`, a fixed `wait()`). Why: counting an empty toast
  container right after a click passes no matter how many toasts arrive later. Test: a guard over test files
  fails on those calls outside a `debug/` helper. Source:
  https://playwright.dev/docs/api/class-frame#frame-wait-for-timeout ("Tests using the timer in production
  are going to be flaky") and https://playwright.dev/docs/best-practices (web-first assertions), verified
  2026-10-31.

- [invariant] Measure; do not eyeball. Decide visual questions with computed values from the real browser and
  compare each number with its threshold before writing a conclusion: text contrast at least 4.5:1, large
  text and UI components at least 3:1, pointer targets at least 24 x 24 CSS px unless an exception applies,
  no horizontal overflow beyond 1 px for the document and each container (including `overflow: hidden`
  ones), fit at the project's smallest supported viewport. At least one element must match before "no
  overflow" means anything. Why: a checker that skipped `overflow: hidden` reported clean while columns
  overflowed by 95 px, and grey text that looked fine measured 2.56:1. Test:
  `python3 "${CLAUDE_SKILL_DIR}/scripts/measure-check.py" check [artifact].json` exits 0, and its
  `self-test` passes. Source: https://www.w3.org/TR/WCAG22/ (1.4.3, 1.4.11, 2.5.8), verified 2026-10-31.

- [invariant] Evidence is element screenshots plus numbers, kept as artifacts. Screenshot the element under
  test (`locator.screenshot()`, or `screenshotElement()` in the Pest plugin), never a full-page shot cropped
  by coordinates. Save screenshots and measurement JSON under a versioned path that CI uploads, not in a temp
  directory. Why: coordinate crops hid the element in question, and screenshots in a temp directory were
  deleted before anyone could repeat the check. Test: the CI job uploads the artifact directory, and every
  path the report names exists. Source: https://pestphp.com/docs/browser-testing (verified 2026-10-31).

- [default] Select copy-driven elements by `data-testid`, and use role plus accessible name where the
  semantics are what you test. Never select by translatable text, class chains or DOM structure. Trade-off:
  test IDs add attributes to production markup and say nothing about accessible names. Deviate only with an
  ADR that names this trade-off. Source: https://playwright.dev/docs/locators#locate-by-test-id (default
  attribute `data-testid`, verified 2026-10-31).

- [default] For push-to-deploy apps, check the production bundle before pushing: build it in a temporary copy,
  run it against a non-production backend, and run the browser checks there. A preview deployment satisfies
  this rule. Trade-off: a production build per change. Deviate only with an ADR that names this trade-off.
  Proof: the report names the build command and the URL the checks ran against.

- [default] Know where the harness differs from a user's browser and check those parts separately. Playwright's
  headless Chromium hides scrollbars, mutes audio, reports a fine pointer with hover, and may render through a
  software GL backend; WebKit in Playwright is not Safari. Trade-off: those behaviours stay unverified in the
  automated run. Deviate only with an ADR that names this trade-off. Source:
  https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/chromium/chromium.ts
  (headless launch arguments, checked in 1.61.1 and 1.64.1, 2026-10-31).

- [default] Use the browser only for what server tests cannot see: props reaching components, client-side
  storage, layout, counts of events, toasts and requests, permission-filtered option lists, dialog gating, CSP.
  Payloads and authorization belong to feature tests. Trade-off: a behaviour seen only in the browser has no
  fast server-side check. Deviate only with an ADR that names this trade-off. Proof: the report maps each
  browser test to one of these categories.

- [default] Run an accessibility scan and walk the primary flow by keyboard on every changed page. Trade-off:
  scans add run time and catch only part of WCAG. Deviate only with an ADR that names this trade-off. Source:
  https://pestphp.com/docs/browser-testing (`assertNoAccessibilityIssues`, default level 1) and
  https://playwright.dev/docs/accessibility-testing (`@axe-core/playwright`; automated tests cannot find every
  violation), verified 2026-10-31.

- [default] Finish edits before a browser run. When a dev build plugin regenerates code from backend files,
  write an import and its use in the same edit; an error overlay is a setup error, so rerun the generator and
  then the test instead of changing the test. Trade-off: a rerun after every edit batch. Deviate only with an
  ADR that names this trade-off. Proof: the preflight checks for an overlay before the first interaction.

- [default] Cover the engines and viewports your users have: public pages in Chromium, Firefox and WebKit plus
  one mobile emulation; dashboards in Chromium at the project's viewport set and in dark mode if the app offers
  it. Trade-off: CI time per engine. Deviate only with an ADR that names this trade-off. Proof: the CI matrix
  and the report list engines and viewports per item.

## Procedure

1. Gate: check that a headless browser can run here (runner installed, browser binaries present). If not,
   stop. Report "not verified in a browser", list what was checked instead, and ask before installing
   anything.
2. Preflight: run the checks in [references/preflight.md](references/preflight.md) and keep the output.
3. Fixture: create the tenant and user through the real path, pass the gates, pin locale and theme, store the
   session.
4. Run headless. Wait for each condition before reading or counting.
5. Assert the absence of failure: errors, failed requests, CSP violations, exact counts, failure signatures.
6. Measure with the collector from [references/measurement.md](references/measurement.md), save the JSON and
   element screenshots to the artifact directory, then run
   `python3 "${CLAUDE_SKILL_DIR}/scripts/measure-check.py" check [artifact].json`.
7. Report per item with [references/evidence-format.md](references/evidence-format.md), including what was not
   verified.

## Traps

- A stale SSR cache served old markup, and correct CSS was doubted twice. Detect: grep the served HTML for the
  change before judging the CSS.
- Dev fixtures sent plain strings where production sends localized objects, so a fix verified against dev data
  rendered `[object Object]` in production. Detect: fixtures built through the real backend path.
- The HMR host was unreachable from the headless browser, the app never mounted, and every test timed out on a
  blank page. Detect: the dev-server marker skip.
- A count read right after a click returned zero toasts and passed. Wait for the expected count instead.
- A component fell back to a generic sentence when its data was missing, and every positive assertion still
  passed. Assert the fallback sentence is absent.
- A half-finished edit broke a code generator; the dev server showed the error overlay to the test browser,
  which surfaced as a 30-second click timeout.
- A scrollbar style existed for months without ever rendering in headless runs. A video whose `currentTime`
  advanced in the headless run showed only black frames in browsers that decode on the GPU. Read pixels from a
  drawn frame instead ([references/harness-differences.md](references/harness-differences.md)).

## Done when

- Every UI item in the report has a command, a result, an artifact path, and the engines and viewports it ran
  on, or is marked "not verified in a browser" with the reason.
- The preflight output is in the report and shows the served artifact contains the change.
- The absence-of-failure checks passed, and `measure-check.py check` exited 0 on the measurement JSON.
- No fixed waits, no headed mode, no user profile in the committed tests.
- Behaviours the harness cannot show (scrollbars, GPU video, real Safari) are listed as not verifiable
  headless.

## References

- [references/preflight.md](references/preflight.md): load before the first browser run in a session, and
  whenever results contradict the source.
- [references/waits-and-selectors.md](references/waits-and-selectors.md): load when writing or fixing a flaky
  browser test.
- [references/measurement.md](references/measurement.md): load for contrast, overflow, fit, target size, or any
  "does it look right" question.
- [references/fixtures-and-identities.md](references/fixtures-and-identities.md): load for authenticated pages,
  gated flows, dark mode, locale pinning and cleanup.
- [references/prod-bundle-check.md](references/prod-bundle-check.md): load for push-to-deploy SSR or static
  sites, or when verifying the production build before a release.
- [references/harness-differences.md](references/harness-differences.md): load for scrollbars, media, GPU,
  WebKit and Safari, hover and pointer media queries.
- [references/evidence-format.md](references/evidence-format.md): load when writing the verification report.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the shared setup, lint
  guards and CI job that enforce these rules.
- [scripts/measure-check.py](scripts/measure-check.py): run with `check`, `contrast` or `self-test`; `--help`
  lists the options.

## Sources

- https://playwright.dev/docs/debug: browsers run headless by default; `headless: false` turns it off, verified
  2026-10-31.
- https://playwright.dev/docs/api/class-frame#frame-wait-for-timeout: fixed waits are for debugging only,
  verified 2026-10-31.
- https://playwright.dev/docs/best-practices: web-first assertions, user-facing locators, verified 2026-10-31.
- https://playwright.dev/docs/locators#locate-by-test-id: `getByTestId` uses `data-testid` by default,
  configurable, verified 2026-10-31.
- https://playwright.dev/docs/accessibility-testing: `@axe-core/playwright` and `AxeBuilder`; automated testing
  cannot detect all WCAG violations, verified 2026-10-31.
- https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/chromium/chromium.ts:
  headless Chromium gets `--hide-scrollbars`, `--mute-audio` and hover and fine-pointer blink settings; same in
  the published 1.61.1 and 1.64.1 bundles, checked 2026-10-31.
- https://pestphp.com/docs/browser-testing: `assertNoJavaScriptErrors`, `assertNoConsoleLogs`,
  `assertNoAccessibilityIssues`, `screenshotElement`, `assertScreenshotMatches`, `--headed`, `inDarkMode`,
  `withLocale`, `--browser firefox|safari`, verified 2026-10-31.
- https://www.w3.org/TR/WCAG22/: contrast 4.5:1 and 3:1 (1.4.3), non-text contrast 3:1 (1.4.11), target size
  24 x 24 CSS px (2.5.8), verified 2026-10-31.
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html: target size exceptions, verified
  2026-10-31.
- https://laravel.com/docs/12.x/vite: the `@vite` directive detects the dev server through the hot file;
  `Illuminate\Foundation\Vite` defaults it to `public/hot` (framework 12.x source), verified 2026-10-31.
