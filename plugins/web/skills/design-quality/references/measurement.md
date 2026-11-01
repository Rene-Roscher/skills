# Measurement

## Contents

- Running the audit
- Reading the output
- Finding levels and thresholds
- Oracle vectors
- Theme, motion and contrast-mode runs
- Screenshots
- When Playwright is not installed
- What the audit does not verify
- Report format

Decide visual questions with numbers, then compare each number with its threshold. A printed value without the
threshold next to it is not a result.

## Running the audit

Run from the project directory so the project's own Playwright is found. The script does not install anything;
without Playwright or its Chromium build it prints what is missing and exits with 2.

```bash
node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --url http://localhost:3000/invoices
node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --url URL --tokens tokens.json --scheme dark
node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --url URL --reduced-motion
node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --url URL --marketing --viewport 1440x900
node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --self-test
```

| Option | Effect |
|---|---|
| `--url` | page to audit; serve a built app, not a dev server with an error overlay |
| `--tokens` | closed token list (format in the tokens reference); omitted means no token check |
| `--scheme dark` | emulates `prefers-color-scheme: dark`; the default is light |
| `--reduced-motion` | emulates `prefers-reduced-motion: reduce` and checks for running animations |
| `--viewport WxH` | default 1440x900; run again at the smallest supported viewport |
| `--marketing` | adds the product-UI and hero-button checks |
| `--self-test` | runs the built-in checks; exit 0 when all pass |

Exit codes: 0 no `fail` finding, 1 at least one `fail`, 2 usage error or Playwright or Chromium missing. JSON goes
to stdout, a one-line summary to stderr.

Run it once per state and per theme: empty, loading, error, partial, populated, worst count, in light and dark.
Every combination is a separate page load. Pages that need a login or seeded data are prepared by the project's
browser-test fixtures; the audit takes a URL and does not log in.

## Reading the output

- `summary`: counts of `fail` and `warn`, and how many text elements were checked for contrast.
- `findings`: `level`, `id`, `selector` (up to three ancestors), `message` with the number, and `value`.
- `typeHistogram`: count per computed font size and `topThreeShare`.
- `radii`, `shadows`, `textColors`: distinct values with counts; the raw material for a token list.
- `spacing`: with a token list, values outside the scale and the share inside it.
- `accentUsage`: with `accent` in the token file, every element that uses it as text, background, border or
  gradient. Read it against the rule that the accent does not decorate.
- `page`: colour scheme and reduced-motion state as the page saw them. Check that they match what you asked for.

## Finding levels and thresholds

| Level | id | Condition | Source |
|---|---|---|---|
| fail | `contrast` | text below 4.5:1, or 3:1 for large text (24 px, or about 18.5 px at weight 700 or more) | WCAG 2.2, 1.4.3 |
| fail | `off-token-*` | font size, weight, family, spacing, radius, shadow or text colour not in the token list | the closed-set rule |
| fail | `nested-radius` | child radius larger than the parent's | the radius rule |
| fail | `target-size` | target under 24 x 24 px with another target or circle within 24 px | WCAG 2.2, 2.5.8 |
| fail | `overflow` | `scrollWidth` exceeds `clientWidth` by more than 1 px, including clipped containers | the overflow rule |
| fail | `transition-all` | `transition-property: all` with a non-zero duration | Web Interface Guidelines |
| fail | `reduced-motion` | running animations with reduced motion requested | Web Interface Guidelines |
| fail | `product-ui`, `hero-buttons` | with `--marketing`: no product UI within 1.3 viewport heights; more than two hero buttons | the marketing rule |
| warn | `contrast-unknown-background` | text over a gradient or image, not measured | limit of the method |
| warn | `type-scatter` | more than five sizes and the top three cover under 60% | design default |
| warn | `untuned-display` | text of 32 px or more with tracking 0 and line height of 1.2 or more | design default |
| warn | `tabular-nums` | numeric table cell without tabular numerals | Web Interface Guidelines |
| warn | `tell-*` | template tells, see the tells reference | design default |

Contrast is computed with the WCAG formula: relative luminance `L = 0.2126 R + 0.7152 G + 0.0722 B` over linearised
sRGB channels, ratio `(L1 + 0.05) / (L2 + 0.05)`, never rounded. The printed value is truncated to two decimals so
4.499 prints as 4.49 and cannot look like a pass. Source: https://www.w3.org/TR/WCAG22/ (definitions of relative
luminance and contrast ratio; the 0.04045 threshold replaced 0.03928 before May 2021, with no practical effect) and
https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html (no rounding; 14 pt and 18 pt are about 18.5 px
and 24 px), verified 2026-11-01.

The target check implements the 2.5.8 spacing exception (a 24 px circle centred on an undersized target meets no
other target or circle). It exempts inline links in running text and browser-drawn controls such as date inputs.
The equivalent-control and essential exceptions need a person: record them in the report.

## Oracle vectors

The self-test fixes these, each computed by hand with the formula above:

| Foreground | Background | Ratio | Verdict at 4.5:1 |
|---|---|---|---|
| `#000000` | `#ffffff` | 21.00 | pass |
| `#767676` | `#ffffff` | 4.542 | pass |
| `#777777` | `#ffffff` | 4.478 | fail |
| `#0000ff` | `#ffffff` | 8.592 | pass |
| `#6b7280` | `#111827` | 3.669 | fail |
| 50% black over white, then `#777777` | | composited to `rgb(127.5, 127.5, 127.5)` first | |

`#777777` is the standard example of a grey that looks fine and fails: 4.478 is below 4.5. The last pair is a muted
grey that passes in a light theme and fails in a dark one.

## Theme, motion and contrast-mode runs

Playwright's `colorScheme`, `reducedMotion`, `forcedColors` and `contrast` options exist on `browser.newContext()`
and on `page.emulateMedia()` (https://playwright.dev/docs/api/class-page, verified 2026-11-01). The audit sets
`colorScheme` and `reducedMotion`. Smoke-test `forcedColors: 'active'` and `contrast: 'more'` by hand: open the
page with each option and confirm text, borders and focus indicators remain visible.

Focus: press Tab through the page; each focused element shows a visible indicator and is not fully hidden by a
sticky header or banner (WCAG 2.2, 2.4.7 and 2.4.11). The audit does not do this walk; the browser test does.

## Screenshots

- Take element screenshots with `locator.screenshot()`, never full-page crops by coordinates.
- Pass `animations: 'disabled'` so captures are stable; Playwright then stops CSS animations, transitions and Web
  Animations (https://playwright.dev/docs/api/class-locator, verified 2026-11-01).
- Capture the reference artifact and the new work at the same viewport and theme, and put them side by side.

## When Playwright is not installed

Do not install it globally. Choose one:

1. Install it in the project as a dev dependency with the project's package manager, then its browser build
   (https://playwright.dev/docs/intro, verified 2026-11-01), and rerun.
2. Run what needs no browser: `node scripts/design_audit.mjs --self-test` proves the check logic on built-in
   samples; the contrast function can be called on colours read from the CSS source. Label those numbers
   "computed from source, not measured in a browser".
3. If neither is possible, report the UI as "implemented, not verified in a browser" and list what was checked
   instead. The status wording follows `browser-verification`.

## What the audit does not verify

- Text over gradients and images (reported as unknown): sample pixels from an element screenshot with the text
  made transparent, or check by hand.
- Colours the script cannot parse. The in-page collector reads colours through a 1 x 1 canvas when a computed
  value is not `rgb()` or `rgba()`; the browser-less functions return no colour for `oklch()`, `lab()` and
  `color()`. Unverified: how each Chromium version serialises computed values in those spaces; the self-test
  covers `rgb()` pages only.
- Pseudo-element text, text in canvas and SVG, shadow DOM contents, and iframes.
- Focus visibility, hit areas enlarged with pseudo-elements, keyboard behaviour, forced-colours rendering.
- Hover and active states: the audit reads the resting page.
- Meaning: whether a component is the right component.
- The self-test's HTML reader is a small regex reader for tell lint on snippets; it is not a CSS engine.

## Report format

Per check: command, numbers, threshold, verdict, artifact path, and what was not verified.

```text
Audit: invoices list, light, 1440x900
  command: design_audit.mjs --url ... --tokens tokens.json
  result: 0 fail, 2 warn; 143 text elements checked for contrast, none below 4.5:1
  warn tell-mono-labels: 3 labels; kept, they are invoice IDs (code-like)
  warn type-scatter: 5 sizes, top three 83%
  not verified: text over the header gradient (unknown background), hover states
  artifacts: shots/invoices-reference.png, shots/invoices-new.png
```
