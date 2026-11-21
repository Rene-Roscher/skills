# Measuring motion

## Contents

- Setup
- The probe helpers
- Pass criteria
- Reading values inside the page
- Reduced motion
- The report

## Setup

The probe resolves Playwright from the project under test, so it uses the project's pinned version and the browsers
installed for it:

```bash
npm install --save-dev playwright        # or the project's package manager
npx playwright install chromium firefox webkit
```

Write a short script next to the project that imports the helpers and drives one surface, then run it once per
engine. Run headless only, never in someone's own browser session.

```js
import { launch, sample, settled, overshoot } from '${CLAUDE_SKILL_DIR}/scripts/probe.mjs';

const browser = await launch(process.argv[2] ?? 'chromium');
const page = await (await browser.newContext({ viewport: { width: 1280, height: 860 } })).newPage();
await page.goto('http://localhost:5173/projects');
// open the surface, then sample it
const frames = await sample(page, '.toast', 1200);
await settled(page, '.toast');
console.log(overshoot(frames, 'w', frames[0].w, frames.at(-1).w));
await browser.close();
```

`PLAYWRIGHT_FROM` points the probe at another directory; `PROBE_CHROMIUM_CHANNEL=chrome` drives an installed Chrome
instead of the bundled Chromium. `node probe.mjs --self-test` checks the pure helpers without a browser.

## The probe helpers

| Helper | What it returns |
|---|---|
| `launch(engine)` | a headless browser; `chromium`, `firefox` or `webkit` |
| `sample(page, selector, ms)` | one sample per frame: box, opacity and translate |
| `settled(page, selector)` | resolves when no finite animation runs on the element or below it |
| `overshoot(samples, key, from, to)` | the peak beyond the target, in percent of the travel |
| `boxes(page, selectors)` and `shift(before, after)` | the largest change in px per element between two moments |
| `drag(page, from, to, options)` | a mouse drag at a set speed, with an optional hold before release |
| `presentation(page, selector)` | the translate on screen now |
| `frames(page, n)` | waits n animation frames |
| `rubberBand(options)` | the resistance curve and its inverse |
| `catchTest(page, selector, options)` | the catch test from the interruption reference |
| `pointerLog(page)` | a log of pointer events, to tell a stuck run from a failing one |

## Pass criteria

| Check | Pass |
|---|---|
| End state | the settled size and position equal the natural ones within 0.5 px |
| Overshoot | within 1 percentage point of the curve's own overshoot; 0 for bounce 0 |
| Layout shift | 0 px for every element that should stay, between before and after |
| Catch: `drift` | at most 0.5 px |
| Catch: `moveError` | at most 0.5 px |
| Catch: dependents | at most 1 px and 0.05 opacity each |
| Catch: `settled` | below 0.5 px, and no drag state left on the element |
| Reduced motion | no element travels; state changes still happen |

Read end values only after `settled()`. A spring keeps moving after its perceptual duration, so a fixed timeout
reads it mid-settle.

## Reading values inside the page

Each `page.evaluate` call costs a round trip, and the element keeps moving meanwhile. Read what has to line up
inside the page: a capture listener on `window` for the value at a press, and a `requestAnimationFrame` loop for
per-frame samples. A capture listener on `window` runs before the component's own handler, so it sees the state the
handler starts from.

When a dev server appends a cache-busting query to modules after a hot reload, a test that needs the app's own
module instance (a toast API, a store) imports it by the URL the page loaded:

```js
const url = performance.getEntriesByType('resource').map((e) => e.name).find((n) => n.includes('/useToast'));
const toast = (await import(url)).useToast();
```

## Reduced motion

Run every check again with `browser.newContext({ reducedMotion: 'reduce' })`. Under reduced motion, `sample()`
should show the state change without travel, and `settled()` should resolve within a few frames.

## The report

One table per surface with a column per engine and a row per check, plus the reduced-motion run. Name what was not
measured and why. A WebKit run whose drag never ended is inconclusive when `pointerLog()` shows no `pointerup`;
report it as such and do not count it as a pass or a failure.
