# Tells of generated UI

## Contents

- How to use this list
- Why the clusters move
- The tells (T1 to T19)
- What the audit detects and what a person decides
- Replacing a tell

A tell is a default that appears regardless of subject. Each one below is legitimate when the brief asks for it
or the content calls for it; it becomes a tell when it shows up unasked. The audit reports candidates as warnings.
A person, comparing against the product's existing artifact, decides.

## How to use this list

1. Run the audit and read the `tell-*` warnings.
2. For each warning, ask: did the brief or the product ask for this, or did it arrive by default?
3. Fix it, or write one sentence in the report explaining why it stays.
4. Then remove one decoration (see the boldness rule in SKILL.md) even if nothing was reported.

## Why the clusters move

Anthropic's post on frontend design explains the cause as distributional convergence: models predict from
statistical patterns in training data, where safe design choices dominate, so unprompted landing pages converge on
"Inter fonts, purple gradients on white backgrounds, and minimal animations"
(https://www.claude.com/blog/improving-frontend-design-through-skills, 2025-11-12, verified 2026-11-01).
The published frontend-design skill lists clusters it wants avoided, including a cream background with a serif
display and a clay accent, near-black with one acid accent, a broadsheet layout, the "SaaS-card kit", and "template
chrome" such as tracked all-caps eyebrows, middle-dot meta strings and arrows on links; it adds that the brief's
own words always win, including when the brief asks for one of these looks
(https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md, verified 2026-11-01).

Banning one cluster moves output to the next one, so a ban list is never complete. For an existing product the
stable answer is to match the product's own artifact, not to be distinctive.

## The tells (T1 to T19)

Source column: FD is the frontend-design skill above; AB is the Anthropic post above; "design judgment" means no
published source, and the item is a review heuristic.

| # | Tell | How to check | Calibration | Source |
|---|---|---|---|---|
| T1 | Purple or indigo gradient on a light page | gradient stops with hue 250 to 290 degrees and saturation of 0.3 or more on a light page (audit: `tell-purple-gradient`) | the Tailwind-indigo origin story is second-hand and not used here | AB, FD |
| T2 | Untuned default font: system or Inter at defaults, tracking 0, one weight | display headings of 32 px or more with tracking 0 and line height 1.2 or more (audit: `untuned-display`) | Inter is fine when tuned; Linear uses Inter with stylistic sets and a display cut | AB, FD |
| T3 | Warm cream background near `#F4F1EA` with a high-contrast serif and a clay accent | compare background and accent hue by eye against the brief | FD notes the accent equals the vendor's own chat accent, so on a user's brief it reads as a tell | FD |
| T4 | Near-black page with one acid-green or vermilion accent | dark page, one saturated accent | dark mode itself is fine; the tell is the default pairing | FD |
| T5 | Broadsheet layout: hairline rules, zero radius, dense columns | radius 0 on every surface plus many 1 px rules | right for a newspaper, wrong for an invoicing app | FD |
| T6 | SaaS-card kit: identical rounded cards, one radius at every level, one soft grey shadow, gradient washes | audit: `tell-one-radius`, `tell-repeated-shadow` | radius follows elevation; shadows belong to floating layers | FD |
| T7 | Tracked all-caps eyebrow above every heading | audit: `tell-eyebrow` (uppercase, positive tracking, directly before a heading) | uppercase captions that label data (units, column headers) encode information and are fine | FD |
| T8 | Meta strings joined by middle dots, "WORD - fragment" labels, an arrow on every link and button | audit: `tell-arrow-links` (half or more of links end in an arrow), `tell-middle-dot-meta` | one arrow on a single "read more" link is fine; the tell is "on every" | FD |
| T9 | Monospace for small data labels | audit: `tell-mono-labels` (three or more short non-code labels) | valid for code, IDs, hashes and log lines | FD |
| T10 | One word of the headline accented: italic, bold, another colour or gradient text | audit: `tell-accent-word`, `tell-gradient-text` | none | FD |
| T11 | Numbered markers 01, 02, 03 on content that is not a sequence | audit: `tell-numbered-markers` | right for steps and timelines | FD |
| T12 | A big number, a small label, supporting stats and a gradient accent as the default hero | stat row plus gradient and no product UI in the first viewport | stats with source and period are proof; stats as decoration are the tell | FD |
| T13 | Fade-and-slide-up on every section, hover transition on every card | audit: `tell-entrance-animations` (four or more elements animating on load) | motion that answers an action (open, expand, confirm) is welcome | FD |
| T14 | Emoji feature tiles, gradient hero, pill buttons, everything centred, stock lines such as "... reimagined" | audit: `tell-emoji-heading`; centring and stock lines by review | each of these reads as stock on its own, and together they read as a template | design judgment |
| T15 | Dark card with radial glow, glowing button, decorative logo in a corner | audit: `tell-glow-card` (radial gradient plus wide shadow) | show the real content as small previews instead | design judgment |
| T16 | An invented style that matches nothing in the product, or the style of a different surface | the report names no reference artifact | the stable fix is the reference-first rule | design judgment |
| T17 | A generic browser frame with grey bars as the product mock-up | the mock-up holds no real component or data | reuse the site's richest existing mock-up language | design judgment |
| T18 | Placeholder data: lorem ipsum, "John Doe", "Acme", round numbers | audit: `tell-placeholder-data` | realistic IDs, durations, amounts and log lines read as real | design judgment |
| T19 | Grey text that "looks fine" | audit: `contrast` in light and dark | one grey judged by eye measured 2.56:1; another passed in light and measured 4.14:1 in dark | design judgment, WCAG 1.4.3 |

Notes on a few rows:

- T2 and the font: the current frontend-design text asks for a deliberate choice of typeface and does not name
  fonts to avoid. Do not rewrite a working product font; tune it.
- T4 and T3 are palette defaults, not detectable by a lint. The report states the palette and its reason.
- T13: the current frontend-design text calls fade-and-slide-up entrances on each section and hover transitions
  on every card "the generic default" and asks for one orchestrated moment instead (FD). Unverified: older
  versions of that text may have advised differently; follow the current one.

## What the audit detects and what a person decides

| Audit finding | Meaning | Decision |
|---|---|---|
| `tell-*` | pattern found in computed styles or visible text | a person: fix, or justify |
| `untuned-display` | display heading with tracking 0 and loose line height | tune it, or justify (one measured site keeps tracking 0) |
| `type-scatter` | text spread across many sizes | fold sizes into the scale |
| `contrast-unknown-background` | text over gradient or image, not measured | sample pixels or check by hand |

The audit never fails on a tell. Failing is reserved for thresholds (contrast, targets, overflow, motion) and the
closed token set.

## Replacing a tell

| Tell | Replace with |
|---|---|
| eyebrow above a heading | nothing; if the label carries information, make it part of the heading or a visible tab |
| accented headline word | one weight and colour for the whole headline; put emphasis in the sentence |
| arrow on every link | arrows only where direction matters (external or forward steps) |
| numbered markers | a list, or real step numbers on real steps |
| grey-bar mock-up | the product's components with realistic data |
| glow card | a plain surface showing the real content |
| entrance animations | one orchestrated moment, or none |
| purple gradient | the product's accent on a neutral surface |
