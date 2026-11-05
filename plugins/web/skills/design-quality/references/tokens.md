# Tokens

## Contents

- The token file the audit reads
- Extracting tokens from an existing artifact
- Type roles
- Spacing
- Radius and shadow by elevation
- Colour roles (tokens from a measured reference, stacking scale)
- Calibration: what measured products do

A token list makes "closed set" checkable. The audit compares every computed value on a page against it and fails
on anything outside. Taste (which sizes, which radii) belongs to the project; this file gives the format and the
measured ranges to calibrate against.

## The token file the audit reads

`design_audit.mjs --tokens tokens.json` accepts any subset of these keys. A missing key skips that check.

```json
{
  "fontSizes": [12, 13, 14, 16, 20, 32, 48],
  "fontWeights": [400, 500, 600],
  "fontFamilies": ["inter", "jetbrains mono"],
  "spacing": [2, 4, 6, 8, 12, 16, 24, 32, 48, 64],
  "radii": [4, 6, 12, 16],
  "shadows": ["rgba(0, 0, 0, 0.08) 0px 0px 0px 1px"],
  "colors": ["#171717", "#4d4d4d", "#0070f3"],
  "accent": "#0070f3",
  "zIndex": [10, 20, 30, 40, 50, 60, 70]
}
```

- `fontSizes`, `spacing`, `radii` are CSS px. Spacing covers padding, margin, row gap and column gap, compared by
  absolute value; 0 always passes.
- `fontFamilies` are first-family names, lower case, without quotes.
- `shadows` are computed `box-shadow` strings exactly as the browser serialises them. Copy them from a first
  audit run rather than typing them.
- `colors` lists allowed text colours only (hex or `rgb()`); `accent` makes the report list every element that
  uses it as text, background, border or gradient.
- `zIndex` lists the steps of the stacking scale; any positioned element with another non-zero `z-index` fails.
- Pills (radius of 999 px or more) are not compared.

Expect the first run on an unstyled page to fail on browser defaults, for example the 0.67 em margin of an `h1`.
That is correct: set the margin from the scale.

## Extracting tokens from an existing artifact

1. Run the audit without `--tokens` on the product's closest existing screen, in light and dark.
2. Read `typeHistogram`, `radii`, `shadows`, `textColors` and `spacing` in the output.
3. Keep values that carry most elements and are used on purpose; fold near-duplicates (13 and 13.5 px, 11 and
   12 px radii) into one token and fix the stragglers.
4. Commit `tokens.json` next to the design tokens of the project, and keep one source of truth: generate the file
   from the CSS variables or the Tailwind theme where that is possible.

## Type roles

Define roles, not sizes. Each step has a fixed size, line height, tracking and weight.

| Role | Use | Notes |
|---|---|---|
| Heading | titles of pages and sections | tracking tightens as size grows |
| Label | single lines: menus, table headers, form labels | line height tuned for icon alignment |
| Copy | text that wraps | higher line height than a label |
| Button | text inside buttons only | weight a notch above body |
| Mono | code, IDs, log lines, inline code | not for ordinary labels |

Measured on Geist's published token classes (computed in Chromium on 2026-11-01 from
https://vercel.com/geist/typography): heading-72 72/72 px, -0.06 em; heading-64 64/64, -0.06 em; heading-48
48/56, -0.06 em; heading-32 32/40, -0.04 em; heading-20 20/26, -0.02 em; heading-14 14/20, -0.02 em; all weight
600. copy-24 24/36, copy-18 18/28, copy-14 14/20, copy-13 13/18, weight 400. label-14 14/20, label-13 13/16,
label-12 12/16. button-16 and button-14 are x/20, button-12 is 12/16, weight 500. The page describes label-14 as
the most common text style used in many menus, copy-14 as the most commonly used text style, label-12 as
tertiary text in busy views, and button-12 as only for a tiny button inside an input.

What to take from it: tracking runs from -0.02 em at 20 px and below to -0.04 em at 32 px and -0.06 em from
40 px up; headings of 48 px and above sit at line height 1.0 to 1.17; body copy is 14 or 16 px.

## Spacing

Pick a scale and report values outside it. Do not demand a strict 4 px grid. Measured on 2026-11-01 (padding,
margin and gap values of visible elements, 1440 x 900): the share on a multiple of 4 px was 20% on Vercel, 61% on
Raycast, 67% on Linear, 72% on Stripe and Resend, and 87% on Laravel's cloud page. All six use a recognisable
scale. Allow 2 px and 6 px steps if the product uses them. An optical correction of 1 px is allowed with a
comment saying why.

## Radius and shadow by elevation

Geist's Materials page (https://vercel.com/geist/materials, verified 2026-11-01) maps surface level to radius:
base and small 6 px, medium and large 12 px, menu and modal 12 px, fullscreen 16 px, tooltip 6 px. Use the idea
(one radius per elevation, nested corners concentric) and choose your own values.

- Nested corners: child radius is at most the parent radius; for a child inset by `p` px, the concentric value
  is `parent radius - p`. The audit fails the first case.
- Shadows: resting surfaces use a border or a 1 px ring; floating layers (menu, popover, dialog) use at least two
  shadow layers. Semi-transparent borders keep edges crisp on tinted backgrounds.

## Colour roles

Geist's colour page (https://vercel.com/geist/colors, verified 2026-11-01) gives two page backgrounds and ten
colour steps per ramp, each with a fixed role: steps 1 to 3 component backgrounds (default, hover, active),
4 to 6 borders (default, hover, active), 7 and 8 high-contrast backgrounds, 9 secondary text and icons, 10 primary
text and icons. In the page's CSS the steps are numbered 100 to 1000 (`ds-gray-100` to `ds-gray-1000`). The role
mapping is the point: fix step roles once and never choose a grey by feel.

Linear generates its themes from three inputs, a base colour, an accent colour and a contrast value, in the LCH
colour space, replacing 98 per-theme variables
(https://linear.app/now/how-we-redesigned-the-linear-ui, verified 2026-11-01). Do the same where themes multiply:
derive surfaces and text from a few inputs and re-check contrast for every output.

### Tokens from a measured reference, one per role

When a reference exists, measure first and write tokens second. For each role, read the computed value from the
reference in light and in dark (element screenshot plus the audit's `textColors`, or `getComputedStyle` on the
element) and record it in a table:

| Role | Reference light | Token light | Reference dark | Token dark | Contrast against its surface |
|---|---|---|---|---|---|
| `--surface` | | | | | |
| `--surface-raised` | | | | | |
| `--border` | | | | | 3:1 only where the border alone marks a control |
| `--input-border` | | | | | 3:1 against the surface (WCAG 1.4.11) |
| `--text` | | | | | 4.5:1 |
| `--text-muted` | | | | | 4.5:1 |
| `--caption` | | | | | 4.5:1 |

Each role is its own token, written with its own value per theme. A border defined as `var(--caption)` or as
`color-mix()` of a text token moves whenever the text token moves: raising caption contrast then lightens every
border in dark mode. Shared values are fine; shared definitions are not. After each change, take element
screenshots of the same component in light and dark next to the reference.

### Stacking scale

One scale, one file, in this order from low to high: base content, raised (sticky headers, floating action),
dropdown and select menus, overlay (sheet, slideover, drawer), modal dialog, popover opened inside a dialog, toast,
tooltip. Components reference the step by name (`z-[var(--z-modal)]`, `z-modal`), never a number. A layer opened
from another layer takes a higher step and is portalled to `<body>`; inside one stacking context a higher number
cannot lift an element above a sibling context.

Rules of thumb: text in two or three neutral steps; one accent hue; status hues only for state; status colour as
text is computed per theme (the dark-theme step usually needs to be lighter than the light-theme step).

## Calibration: what measured products do

Computed styles of the first `h1`, `h2` and paragraph, headless Chromium 156, viewport 1440 x 900, one run on
2026-11-01 (sites change; treat as a snapshot):

| Site | h1 size / line height / tracking / weight | Family |
|---|---|---|
| Linear | 64 / 64 px / -0.022 em / 510 | Inter Variable |
| Vercel | 64 / 64 px / -0.06 em / 400 | Geist |
| Laravel (cloud page) | 60 / 60 px / -5% / 500 | Instrument Sans |
| Stripe (en-us) | 48 / 55.2 px / -0.02 em / 300 | Sohne |
| Raycast | 64 / 70.4 px / 0 / 600 | Inter |
| Resend | 96 / 96 px / -0.01 em / 400 | a display serif |

Five of six use line height 1.0 to 1.15 with negative tracking; none uses weight 700 or above on the h1; Raycast
is the exception on tracking. Inter appears on three of six, so the family alone does not separate careful from
generic; the tuning does. Same run: the three most common font sizes covered 65% (Raycast), 72% (Stripe, Laravel),
79% (Linear), 91% (Vercel) and 95% (Resend) of text elements; the number of distinct text colours ranged from 7
(Vercel) to 26 (Laravel).

Copy the restraint, not the contrast values: earlier measurements on the same sites found text below WCAG
thresholds in placeholders, chart axes and mock-ups (2026-10-31, not re-run).
