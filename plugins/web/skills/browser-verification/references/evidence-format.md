# Evidence format

The verification write-up says per item what ran, what came out, where the evidence is, and what was not
verified. "Tests green" and "seen working" are different statuses.

## Template

```markdown
## Verification: [change]

Preflight
  target:     built assets
  served:     /invoices contains 'data-testid="invoice-total"' 1 time(s)
  overlay:    none in served HTML
  locale:     de-DE (user record and browser)   theme: dark (app setting)

| Item | Command | Result | Evidence | Engines and viewports |
|---|---|---|---|---|
| Invoice table does not overflow | `npx playwright test tests/e2e/invoices.spec.ts` | PASS: overflow 0px | `tests/Browser/artifacts/invoices-1024.png`, `tests/Browser/artifacts/measure-chromium.json` | chromium; 1024x700, 1280x720 |
| Muted text readable on dark cards | `python3 .../measure-check.py check tests/Browser/artifacts/measure-chromium.json` | FAIL: 3.03:1 (needs 4.5:1) | `tests/Browser/artifacts/billing-card-dark.png` | chromium; 1280x720 |
| Save sends one request | same spec, test "saves once" | PASS: 1 POST, 1 toast | trace in `tests/Browser/artifacts/` | chromium |

Not verified
- Scrollbar styling: scrollbars are hidden in headless Chromium; needs a headed check.

Status: tested and seen in a headless browser. Not deployed.
```

## Rules for the write-up

- Every item has a command, a result with numbers where numbers exist, and at least one artifact path that
  exists in the repository's artifact directory.
- A failing measurement is reported as a failure with its number, even when the change was meant to fix it.
- An item without browser evidence says "implemented, not verified in a browser" and gives the reason and what
  was checked instead.
- Behaviours the harness cannot show are listed under "Not verified".
- The status line uses the project's status words (for example implemented, tested, verified, deployed, live).
  A UI item reaches "verified" only with browser evidence.
- Paste `measure-check.py` output lines unchanged. Do not round ratios up.

## When no browser could run

```markdown
Not verified in a browser: no browser binaries in this environment, and installing them needs approval.
Checked instead: read `ConfirmDialog.vue` (the close handler now emits `close`), ran the component unit test
(green). Remains for a browser run: click the close button, assert the dialog is gone and focus returns to the
trigger, no JavaScript errors.
```
