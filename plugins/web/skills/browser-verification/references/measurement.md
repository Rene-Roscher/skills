# Measurement

## Contents

- Thresholds
- The collector
- Running it
- Checking the numbers
- Limits of the collector
- Testing your own helpers

Visual questions are decided with numbers read from the real browser, compared with a threshold before any
conclusion is written. Copy the collector below into the project (for example
`tests/Browser/Support/measure.js`) so it is versioned with the tests, and check its output with the bundled
`measure-check.py`.

## Thresholds

| Check | Pass when | Source |
|---|---|---|
| Text contrast | at least 4.5:1 | WCAG 2.2, 1.4.3 |
| Large-scale text (at least 18 pt, or 14 pt bold; 24 px or 18.67 px bold) | at least 3:1 | WCAG 2.2, 1.4.3 |
| UI components and graphical objects | at least 3:1 against adjacent colours | WCAG 2.2, 1.4.11 |
| Pointer target size | at least 24 x 24 CSS px, unless an exception (spacing, inline, essential) applies | WCAG 2.2, 2.5.8 |
| Horizontal overflow | `scrollWidth - clientWidth` at most 1 px, and no descendant clipped by more than 1 px | subpixel tolerance |
| Fit | the element's bottom edge at most the viewport height | the project's smallest supported viewport |

Sources: https://www.w3.org/TR/WCAG22/ and
https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html (verified 2026-10-31).

Never round a ratio up before comparing. 4.497:1 fails 4.5:1. The checker compares the unrounded value and
truncates what it prints.

## The collector

```js
// tests/Browser/Support/measure.js
// Runs inside the page. Returns JSON for measure-check.py.
// spec: { overflow: [css], contrast: [css], targets: [css], fit: [css], ignore: [css] }
export function measure(spec) {
  const ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true })
  ctx.canvas.width = ctx.canvas.height = 1
  const read = () => { const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data; return `rgb(${r}, ${g}, ${b})` }
  const round = (n) => Math.round(n * 10) / 10
  const ignored = (el) => (spec.ignore || []).some((s) => el.closest(s))
  const visible = (el) => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el)
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'
  }
  const backdrop = () => {
    const p = document.createElement('div')
    p.style.backgroundColor = 'Canvas'
    document.documentElement.appendChild(p)
    const c = getComputedStyle(p).backgroundColor
    p.remove()
    return c
  }
  const paintBackground = (el) => {
    const layers = []
    let uncertain = null
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const s = getComputedStyle(n), tag = n.tagName.toLowerCase()
      if (s.backgroundImage !== 'none') uncertain ||= `background image on ${tag}`
      if (parseFloat(s.opacity) < 1) uncertain ||= `opacity ${s.opacity} on ${tag}`
      if (s.filter !== 'none' || s.mixBlendMode !== 'normal') uncertain ||= `filter or blend mode on ${tag}`
      layers.push(s.backgroundColor)
    }
    ctx.globalCompositeOperation = 'copy'
    ctx.fillStyle = backdrop()
    ctx.fillRect(0, 0, 1, 1)
    ctx.globalCompositeOperation = 'source-over'
    for (const c of layers.reverse()) { ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1) }
    return uncertain
  }
  const insideScroller = (d, root) => {
    for (let n = d.parentElement; n && n !== root; n = n.parentElement) {
      const ox = getComputedStyle(n).overflowX
      if (ox === 'auto' || ox === 'scroll') return true
    }
    return false
  }
  const each = (sels, fn) => (sels || []).flatMap((sel) =>
    [...document.querySelectorAll(sel)].filter((el) => visible(el) && !ignored(el))
      .map((el, i, all) => ({ selector: all.length > 1 ? `${sel} [${i}]` : sel, ...fn(el) })))

  const out = { page: location.pathname, viewport: { width: innerWidth, height: innerHeight } }
  if (spec.overflow) out.overflow = each(spec.overflow, (el) => {
    const box = el.getBoundingClientRect()
    let clipped = 0
    for (const d of el.querySelectorAll('*')) {
      if (!visible(d) || ignored(d) || insideScroller(d, el)) continue
      const r = d.getBoundingClientRect()
      clipped = Math.max(clipped, r.right - box.right, box.left - r.left)
    }
    return { scrollWidth: el.scrollWidth, clientWidth: el.clientWidth, clippedPx: round(clipped) }
  })
  if (spec.contrast) out.contrast = each(spec.contrast, (el) => {
    const s = getComputedStyle(el)
    const uncertain = paintBackground(el)
    const bg = read()
    ctx.fillStyle = s.color
    ctx.fillRect(0, 0, 1, 1)
    const pt = parseFloat(s.fontSize) * 0.75, bold = parseInt(s.fontWeight, 10) >= 700
    return { fg: read(), bg, large: pt >= 18 - 1e-3 || (bold && pt >= 14 - 1e-3), uncertain,
             text: (el.textContent || '').trim().slice(0, 40) }
  })
  if (spec.targets) out.targets = each(spec.targets, (el) => {
    const r = el.getBoundingClientRect()
    return { width: round(r.width), height: round(r.height) }
  })
  if (spec.fit) out.fit = each(spec.fit, (el) => ({ bottom: round(el.getBoundingClientRect().bottom), limit: innerHeight }))
  return out
}
```

The canvas readback turns any CSS colour syntax (`oklch()`, `color()`, named colours) into the 8-bit sRGB value
the page paints, and composites semi-transparent layers the same way. The page backdrop comes from the `Canvas`
system colour, which follows `color-scheme`, so a dark scheme without an explicit background is measured
against the dark backdrop.

## Running it

Pass the function to the page evaluation call; do not inject it as a script tag, which a strict CSP blocks.

```ts
import { measure } from './Support/measure.js'
import { writeFileSync, mkdirSync } from 'node:fs'

const result = await page.evaluate(measure, {
  overflow: ['html', '[data-testid="invoice-table"]'],
  contrast: ['[data-testid="card-muted"]'],
  targets: ['button', 'a[role="button"]'],
  fit: ['[data-testid="dialog"]'],
  ignore: ['[data-testid="offcanvas-menu"]'],
})
mkdirSync('tests/Browser/artifacts', { recursive: true })
writeFileSync(`tests/Browser/artifacts/measure-${testInfo.project.name}.json`, JSON.stringify(result, null, 2))
```

With the Pest browser plugin, evaluate the same function source through the plugin's JavaScript evaluation
method and write the returned array to the artifact directory.

Measure at every viewport the project supports, and wait for the element first (see the waits reference).

## Checking the numbers

```sh
python3 "${CLAUDE_SKILL_DIR}/scripts/measure-check.py" check tests/Browser/artifacts/measure-chromium.json \
  --require overflow,contrast
python3 "${CLAUDE_SKILL_DIR}/scripts/measure-check.py" contrast 'rgb(107, 114, 128)' 'rgb(31, 41, 55)'
```

Each line prints `PASS`, `FAIL` or `UNDECIDED` with the value and the threshold. The exit code is 1 when any
item fails or cannot be decided. A requested kind with no matching element fails: a check over zero elements
proves nothing. Paste the output into the report.

## Limits of the collector

- The background walk follows ancestors only. Text over an absolutely positioned sibling, a pseudo-element or
  an image is not seen. The collector marks background images, opacity, filters and blend modes as uncertain;
  for those, sample pixels from the element screenshot instead.
- Contrast is measured for the element's own `color`. Measure each text element, not the card around it.
- Off-canvas or intentionally clipped content shows up as clipped. Exclude it with `ignore` and say so in the
  report.
- Overflow inside a horizontal scroll container is treated as reachable and not counted. If the design must not
  scroll, measure the scroll container itself.

## Testing your own helpers

If the project keeps its own contrast or overflow helper, test it against an independent implementation, not
against itself. `measure-check.py contrast` is one: feed both the same colour pairs and compare the ratios.
Known vectors: black on white 21:1, `#767676` on white 4.54:1 (passes), `#777777` on white 4.47:1 (fails).
`measure-check.py self-test` runs these.
