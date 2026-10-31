# Waits and selectors

## Waits

Wait for the condition you are about to assert. Then read or count.

| Need | Playwright Test | Pest browser plugin |
|---|---|---|
| element appears | `await expect(locator).toBeVisible()` | `assertPresent`, `assertSee` |
| exact count | `await expect(locator).toHaveCount(n)` (retries until equal) | assert after the presence assertion |
| a request finished | `await page.waitForResponse((r) => ...)` | assert on the UI state the response produces |
| element gone | `await expect(locator).toHaveCount(0)` or `toBeHidden()` | the plugin's absence assertions |
| anything else | `await expect.poll(() => value).toBe(expected)` | a retrying assertion, never a fixed `wait()` |

Check in the Pest docs which assertions retry for your plugin version
(https://pestphp.com/docs/browser-testing, verified 2026-10-31).

Never: `page.waitForTimeout(ms)`, `sleep`, `usleep`, a fixed `wait(seconds)`. Playwright documents fixed
timeouts as debugging aids that make tests flaky
(https://playwright.dev/docs/api/class-frame#frame-wait-for-timeout, verified 2026-10-31). A fixed wait that
is long enough on one machine is too short on a loaded CI runner.

## Counting without sampling too early

Counts need an end signal: the UI state that exists only after the action finished.

```ts
const posts: string[] = []
page.on('request', (r) => { if (r.method() === 'POST' && r.url().includes('/invoices')) posts.push(r.url()) })

await page.getByTestId('invoice-save').dblclick()
await expect(page.getByTestId('toast')).toHaveCount(1)          // retries until exactly one
await expect(page.getByTestId('invoice-save')).toBeEnabled()    // end signal: the submit finished
expect(posts).toHaveLength(1)                                    // one POST per submit
await expect(page.getByTestId('toast')).toHaveCount(1)          // still one after the end signal
```

Reading `toast` count right after the click returns zero, which passes a "not two toasts" check no matter what
arrives later.

## Selectors

| Element | Select by | Why |
|---|---|---|
| copy-driven or translated text, marketing-owned blocks | `getByTestId('invoice-total')` | wording and locale change; the test ID does not |
| controls whose semantics you test | `getByRole('button', { name: 'Save' })` | proves it is a button with that accessible name |
| form fields | `getByLabel(...)` or test ID | label text is copy; prefer the test ID when copy is volatile |
| never | `text=`, `has-text(`, CSS class chains, `nth-child` paths | break on copy edits, locale switches and design work |

`getByTestId` uses the `data-testid` attribute by default, and `testIdAttribute` changes it
(https://playwright.dev/docs/locators#locate-by-test-id, verified 2026-10-31). Playwright's best practices
prefer user-facing locators such as roles (https://playwright.dev/docs/best-practices). The two fit together:
roles where semantics are under test, test IDs where copy is volatile.

Test IDs name the thing, not its look: `invoice-total`, not `blue-number-right`.

## Fixing a flaky test

1. Run it repeatedly headless (`--repeat-each` in Playwright) and keep the failure output.
2. Find the read that happens before its condition: a count, a text read, a screenshot, a measurement.
3. Put a retrying assertion on that condition in front of the read.
4. Remove every fixed wait the test had.
5. Run it repeatedly again and report the before and after pass counts.
