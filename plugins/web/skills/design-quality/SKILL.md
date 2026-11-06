---
name: design-quality
description: "Makes product and marketing UI look made with care, not generated: match the existing artifact first, closed token sets for type, spacing, radius and colour, one accent, WCAG contrast, every state designed, real icons instead of emoji, no template tells, all measured in a browser. Use when designing, restyling or reviewing a page, dashboard, table, form, empty state or landing hero. Not for test mechanics or copywriting."
license: Apache-2.0
compatibility: "Any web frontend. The bundled audit needs Node 18 or later and Playwright already installed in the project with its Chromium build; tested with Playwright 1.64.1."
metadata:
  author: "Rene Roscher"
---

# Design quality

This skill decides how product and marketing UI should look and how to prove it. Products that look made with
care share restraint and consistency: closed token sets, one accent, quiet chrome, designed states, real content.
Generated templates share the opposite: defaults, decoration and invented data. Browser measurement is in
`browser-verification`, rendering in `web-architecture`. The failure this prevents: a screen that looks generated,
or that was approved by eye and fails contrast, overflows with real data, or ignores its product.

## Applies when / does not apply

- Applies: designing or restyling a page, dashboard, table, form, settings screen, empty, loading or error state,
  command palette, chart, dialog or landing section; reviewing a design for a generic look; choosing type,
  spacing, radius, shadow or colour tokens; a hero, pricing or feature page; dark mode.
- Does not apply: browser test mechanics, waits, fixtures and the measurement collector (`browser-verification`),
  rendering strategy and CSP (`web-architecture`), marketing copy and headlines as words, performance budgets,
  and brand identity work (logo, naming).

## Rules

Most important first. Examples use an invoicing app, a project tool and a booking system.

- [invariant] Decide visual questions with numbers from a real browser and element screenshots, never by eye:
  computed type, spacing, radius, shadow and colour against the token list, contrast against WCAG, and the new
  element next to its reference at the same viewport and theme. Why: a grey judged readable by eye measured
  2.56:1. Test: the review holds the audit JSON, the `browser-verification` measurement and element screenshots,
  and `node "${CLAUDE_SKILL_DIR}/scripts/design_audit.mjs" --self-test` passes. Source: WCAG 2.2, 1.4.3
  (https://www.w3.org/TR/WCAG22/, verified 2026-11-01).
- [invariant] Meet the WCAG 2.2 AA floor in every theme: text at least 4.5:1, large text (at least 24 px, or
  about 18.5 px bold) at least 3:1, component boundaries, focus indicators and chart marks at least 3:1 against
  adjacent colours, pointer targets at least 24 × 24 CSS px unless an exception applies, a visible focus
  indicator that sticky content does not fully cover, and never colour alone to carry meaning. Ratios are not
  rounded: 4.499:1 fails. Why: failures cluster where designs soften on purpose: placeholders, tertiary
  metadata, chart axes, mock-ups and brand colour used as text. Test: run the `browser-verification` measurement
  in light and dark; every text element passes, and every status shown in colour also has a label or icon.
  Source: WCAG 2.2, 1.4.1, 1.4.3, 1.4.11, 2.4.7, 2.4.11, 2.5.8 (https://www.w3.org/TR/WCAG22/); "4.499:1 would
  not meet the 4.5:1 threshold" (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html); both
  verified 2026-11-01.
- [invariant] Design and fixture every state of a data view: empty, loading, error, partial (some data failed,
  is stale or is cut off), no permission, limit reached, one item, and the worst realistic count with very long
  names. Every state says what happened and offers a next step. Why: undesigned states render blank screens and
  dead ends, and a dashboard drawn with three sample rows said nothing when a real account had several hundred.
  Test: one fixture per state, one element screenshot each, and a 200-character customer name passes the
  overflow check. Source: Web Interface Guidelines: "All states designed. Empty, sparse, dense, & error states.",
  "No dead ends. Every screen offers a next step or recovery path."
  (https://github.com/vercel-labs/web-interface-guidelines, verified 2026-11-01).
- [invariant] A shortcut on a single letter, digit or punctuation key can be turned off, remapped to include a
  modifier, or works only while its component has focus; every shortcut also exists as a visible control. Why:
  voice input turns speech into letters and fires such shortcuts by accident. Test: with the shortcut setting
  off, pressing the key in the page body does nothing; each shortcut has a menu item or button. Source: WCAG 2.2,
  2.1.4, Level A (https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html, verified 2026-11-01).
- [invariant] Tooltips hold text only. Links, buttons and copy actions go into a non-modal popover that opens on
  hover, focus and click. Why: tooltips never take focus, so keyboard and touch users cannot reach what is inside.
  Test: a lint over component files fails on focusable elements inside the tooltip component. Source: ARIA APG
  tooltip pattern: "Tooltip widgets do not receive focus." and "A hover that contains focusable elements can be
  made using a non-modal dialog." (https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/, verified 2026-11-01).
- [invariant] What the agent writes never contains emoji or pictographic characters, anywhere: not in UI
  strings, status marks, ratings, close buttons, arrows on buttons, feature tiles, headings or country flags, and
  equally not in docs, READMEs, code comments, mails, notifications, CLI output or invented test data. A visual
  that should look like an icon or emoji is a real asset: an icon from the project's set (for example Lucide) or
  an SVG file (an SVG emoji set, SVG flags next to the language or country name), sized from the type scale.
  Input is different: an emoji a user typed into a form, a message or a request is stored, rendered and exported
  as entered, never stripped. Why: emoji come from each platform's colour font, so they ignore the theme and the
  colour tokens, differ between systems, and Windows draws a flag as two letters. Test: `design_audit.mjs` fails
  on `emoji-glyph` and `symbol-icon` outside `data-user-content`; the codepoint scan in references/app-ui.md
  finds nothing in the changed files; a form test saves and renders a user's emoji unchanged. Source: Unicode
  Technical Standard 51, 2.2, "The set of supported emoji sequences may vary by platform."
  (https://www.unicode.org/reports/tr51/); https://bugzilla.mozilla.org/show_bug.cgi?id=1970980 comment 6, "Segoe
  UI Emoji does not provide ligatures for the Regional-Indicator codepoints"; both verified 2026-11-05.
- [invariant] Global and base styles live in a cascade layer: resets, element defaults and global focus rings in
  `@layer base`, component classes in `@layer components` (Tailwind CSS v4), never as plain CSS beside the
  framework's layers. Why: normal declarations outside any layer beat every layered declaration whatever their
  specificity, so one unlayered `:focus-visible` rule overrides every focus utility in the app, and the fix gets
  hunted in specificity instead of in the layer. Test: a control with a `focus-visible:` utility, focused by
  keyboard in the browser, computes the utility's ring, not the global one; `design_audit.mjs` reports no
  `unlayered-css` warning, or each listed rule has a reason (third-party CSS). Source: MDN `@layer`, "Styles that
  are not defined in a layer always override styles declared in named and anonymous layers."
  (https://developer.mozilla.org/en-US/docs/Web/CSS/@layer); Tailwind CSS, base styles in `@layer base`,
  component classes in `@layer components` "that you'd still like to be able to override with utility classes"
  (https://tailwindcss.com/docs/adding-custom-styles); both verified 2026-11-05.
- [invariant] Every number on a marketing page is true and traceable: it names subject, unit and period ("[count]
  invoices sent in [month, year]"), and a claims file in the repo holds its source and the date it was checked.
  No invented customer counts, uptime figures, ratings or growth rates. Why: an invented figure is a false
  statement to buyers, and placeholder numbers in mock-ups survive into production. Test: CI extracts every
  digit-bearing sentence from marketing pages and fails on one without a claims entry. Source: reproducible with
  the test above.
- [invariant] Social proof comes only from real customers who agreed: logos, quotes and case studies with
  permission, quotes attributed to a real person and role, no reviews bought on condition of their sentiment, no
  undisclosed insider reviews, no fake follower counts. Not legal advice. Why: the US rule on reviews and
  testimonials prohibits each of these. Test: every logo and quote has a permission entry in the claims file.
  Source: FTC Consumer Reviews and Testimonials Rule, §§ 465.2 to 465.8, in effect since 2024-10-21
  (https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers,
  verified 2026-11-01).
- [default] Start from the existing artifact of the same type: before designing a screen, table, form, mail or
  marketing section, open the product's existing one of that kind, capture an element screenshot and its computed
  tokens, and reuse its components and structure. A landing page is not the reference for an app screen, and the
  app is not the reference for a mail. Without an artifact of that type, take the closest one and say which.
  Trade-off: less room for a new visual direction. Deviate only with an ADR that names this trade-off. Proof: the
  review names the reference, shows both element screenshots side by side, and the audit finds no value outside
  the token list. Source: frontend-design skill, "Where the brief pins down a visual direction, follow it
  exactly" (https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md, verified 2026-11-01).
  `feature-delivery` carries the same rule.
- [default] For a new surface, pick two or three outside references for its surface type from
  [references/design-references.md](references/design-references.md), name the principle each contributes
  (density, hierarchy, states, motion, copy tone), and measure the result against them like the product's own
  artifact, which stays the first reference. Take principles only, never a brand's look, logo or copy.
  Trade-off: one more step and a pull toward well-known products. Deviate only with an ADR that names this
  trade-off. Proof: the plan names the references; the review compares at least one measured value. Source:
  the systems in references/design-references.md, verified 2026-11-03.
- [default] Keep a closed token set: every computed font size, weight, family, spacing value, radius, shadow and
  colour is a token. An off-token value is replaced or added as a token on purpose; an optical 1 px correction
  carries a comment. Trade-off: every new value costs a token change. Deviate only with an ADR that names this
  trade-off. Proof: `design_audit.mjs --tokens tokens.json` exits 0. Source: Web Interface Guidelines, "Optical
  alignment. Adjust ±1px when perception beats geometry." (verified 2026-11-01).
- [default] Theme tokens come from measurements, one token per role. When a reference exists (the product's
  artifact, a screenshot from the owner, a brand guide), measure its surfaces, borders, input borders, text and
  muted text in light and dark first, then write both themes from those numbers. Each role has its own token with
  its own value per theme; no role is defined through another role's token, so raising caption contrast cannot
  lighten every border. After every visual change, element screenshots in light and dark sit next to the
  reference. Trade-off: more tokens to maintain. Deviate only with an ADR that names this trade-off. Proof: the
  measurement table from references/tokens.md (role, reference value, token value, per theme) is in the review,
  and no border or surface token is defined with `var()` or `color-mix()` of a text token. Source: Geist colour
  step roles (https://vercel.com/geist/colors, verified 2026-11-01); reproducible with the proof above.
- [default] Interactive controls get a state matrix before any styling: for each control type, which of default,
  hover, focus-visible, active, disabled, invalid and checked or pressed change, and to which tokens, in both
  themes. Focus uses `:focus-visible`; hover is never the only cue. Trade-off: one table per control type before
  the first class. Deviate only with an ADR that names this trade-off. Proof: the matrix in the plan (template in
  references/app-ui.md) and an element screenshot per state and theme. Source: WCAG 2.2, 1.4.11 and 2.4.7
  (https://www.w3.org/TR/WCAG22/, verified 2026-11-01); the matrix itself is design judgment.
- [invariant] Overlays follow one written layer hierarchy, low to high: page, raised (sticky header), sheet
  (slideover, drawer), modal, confirm, anchored popover and menu, toast, tooltip; each step is a named z-index
  token. A child layer always stacks above the layer that opened it and is portalled to `<body>`; only the
  topmost layer traps focus and closes on Escape, and focus returns to the opener. No two open layers share a
  step: a sheet never opens a second sheet, a modal never opens a second content modal (it replaces its content
  or opens a confirm). Why: a dialog under its opener cannot be used, and a z-index picked per component breaks
  the first time two overlays meet. Test: a browser test opens each allowed chain (sheet then confirm, modal then
  menu), finds the child topmost at its centre (`document.elementFromPoint`), presses Escape once and finds only
  the child closed and focus on its opener; the audit with `zIndex` tokens reports no `off-token-zIndex`. Source:
  WAI-ARIA APG dialog pattern, focus contained in the dialog and returned on close
  (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/, verified 2026-11-06); the order is design judgment,
  table in references/app-ui.md.
- [default] Type comes from a role-based scale: heading, label (single line), copy (multi-line), button and mono
  roles, each step with fixed size, line height, tracking and weight. Headings from 32 px up get a line height of
  about 1.0 to 1.2 and negative tracking; reading copy stays at 16 px. Most text sits in two or three sizes.
  Trade-off: fewer sizes, so hierarchy comes from weight and colour. Deviate only with an ADR that names this
  trade-off. Proof: the audit's type histogram, the share of text in the top three sizes, and warnings for
  untuned display headings. Source: Geist typography roles (https://vercel.com/geist/typography, verified
  2026-11-01); measured calibration in references/tokens.md.
- [default] One neutral ramp with fixed step roles, text in two or three neutral steps, and exactly one accent hue
  for links, primary actions, selection, focus and highlighted data. Status hues mark state only. The accent does
  not decorate (glows, gradient washes, borders without meaning). Brand colour as text is computed before use.
  Trade-off: less brand colour in the UI. Deviate only with an ADR that names this trade-off. Proof: the audit
  lists distinct text colours and every element using the accent. Source: Geist colours, steps 1–3
  component backgrounds, 4–6 borders, 9 secondary text, 10 primary text, numbered 100–1000 in its CSS
  (https://vercel.com/geist/colors); Linear
  themes from three inputs: base colour, accent colour, contrast
  (https://linear.app/now/how-we-redesigned-the-linear-ui); both verified 2026-11-01.
- [default] Radius follows elevation: one radius per surface level (for example 6 px controls, 12 px cards and
  dialogs, 16 px sheets), pills only on purpose, nested corners concentric with the child radius at most the
  parent's. Trade-off: one more decision per surface type. Deviate only with an ADR that names this trade-off.
  Proof: the audit's radius histogram and zero `nested-radius` findings. Source: https://vercel.com/geist/materials;
  Web Interface Guidelines, "Child radius ≤ parent radius & concentric so curves align."; verified 2026-11-01.
- [default] Build structure from borders and space; shadows belong to floating layers (menus, popovers, dialogs,
  at least two shadow layers), never one soft grey shadow under every card. Trade-off: flatter surfaces. Deviate
  only with an ADR that names this trade-off. Proof: the audit lists distinct shadows and warns on one shadow
  repeated across sibling cards. Source: Web Interface Guidelines, "Mimic ambient + direct light with at least two
  layers."; frontend-design skill, "the SaaS-card kit"; verified 2026-11-01.
- [default] App screens are dense and the chrome recedes: most UI text at 14 px, secondary text at 13 and 12 px in
  busy views, sidebars a few notches dimmer than the work area but still at least 4.5:1, dividers only where they
  separate something, fewer and smaller icons. Trade-off: less touch room on desktop layouts. Deviate only with an
  ADR that names this trade-off. Proof: the audit's type histogram and a separator count before and after.
  Source: https://vercel.com/geist/typography (label-14, label-12); Linear, sidebar "a few notches dimmer"
  (https://linear.app/now/behind-the-latest-design-refresh); verified 2026-11-01.
- [default] Numbers line up: compared figures use tabular numerals, a non-breaking space joins number and unit,
  and one context shows currency with either 0 or 2 decimals. Trade-off: wider figures, so only where compared.
  Deviate only with an ADR that names this trade-off. Proof: compared cells compute `font-variant-numeric:
  tabular-nums`. Source: Web Interface Guidelines, "Tabular numbers for comparisons" (verified 2026-11-01).
- [default] Motion explains cause and effect: animate `transform` and `opacity`, list transition properties and
  never use `transition: all`, provide a reduced-motion variant, keep animations interruptible, and do not
  animate every section in. Trade-off: fewer showcase moments. Deviate only with an ADR that names this
  trade-off. Proof: zero `transition-all` findings; with `--reduced-motion` the audit counts no running
  animations. Source: Web Interface Guidelines, "Never `transition: all`.", "Honor `prefers-reduced-motion`.";
  frontend-design skill lists "fade-and-slide-up entrances on each section"; verified 2026-11-01.
- [default] Spend boldness in one place: one memorable element per view, everything around it quiet, and one
  decoration removed before shipping. Trade-off: less to show off. Deviate only with an ADR that names this
  trade-off. Proof: the review names the bold element and justifies any second treatment. Source: frontend-design
  skill, "Spend your boldness in one place." (verified 2026-11-01).
- [default] Remove generated-template tells unless the brief asks for one: purple gradients on white, an untuned
  default font, tracked all-caps eyebrows everywhere, one accented headline word, identical soft-shadow cards, an
  arrow character on every link, middle-dot meta strings, mono for non-code labels, 01 / 02 / 03 on non-steps, a
  big-number hero without the product, entrance animations on every section, glowing dark cards, grey-bar browser
  frames, placeholder data. Trade-off: a kept tell needs a written reason. Deviate only with an ADR that names
  this trade-off. Proof: the audit's tell warnings, each fixed or justified (references/tells.md). Source:
  https://www.claude.com/blog/improving-frontend-design-through-skills and the frontend-design skill's pattern
  list, verified 2026-11-01.
- [default] Marketing pages show the product: real product UI with realistic data in or just below the first
  viewport, one headline, one supporting sentence, at most two calls to action that say what happens, sentence
  case. Trade-off: a well-known brand may choose an abstract hero. Deviate only with an ADR that names this
  trade-off. Proof: `data-testid="product-ui"` visible within 1.3 viewport heights; at most two hero buttons.
  Source: frontend-design skill, "A CTA says exactly what happens when it is used"; Web Interface Guidelines, "On
  marketing pages, use sentence case."; verified 2026-11-01.
- [default] App components follow their patterns: tables keep filters, sort and page in the URL and truncate in
  fixed columns with the full value reachable; forms label every control and focus the first error; a command
  palette is a combobox with a listbox popup; tooltips come from the design system, not `title`; charts use
  colour-blind-friendly palettes with a second cue. Trade-off: more markup and tests per component. Deviate only
  with an ADR that names this trade-off. Proof: the checks in references/app-ui.md. Source: Web Interface
  Guidelines; https://www.w3.org/WAI/ARIA/apg/patterns/combobox/; MDN on `title`; all verified 2026-11-01.

## Procedure

1. Gate: name the existing artifact of the same type and capture it (element screenshot, computed tokens). If
   none exists, name the closest one and say so. For a new surface, also name two or three outside references
   for its surface type from [references/design-references.md](references/design-references.md). Do not
   design before this step.
2. Measure the reference's values per role in light and dark, then write or extract the token list
   (`tokens.json`, format and measurement table in [references/tokens.md](references/tokens.md)), one token per
   role, plus the stacking scale. Record project taste (density, radii, viewports) in the project overlay profile,
   not in components.
3. List the states the view needs (empty, loading, error, partial, no permission, limit reached, one item, worst
   count) and build a fixture for each before styling. Write the state matrix for each interactive control type
   and place every overlay on the layer hierarchy. Check that global CSS sits in a layer.
4. Build with the product's components, tokens and icon set (no emoji, no characters as icons), app screens per
   [references/app-ui.md](references/app-ui.md), marketing pages per
   [references/marketing-pages.md](references/marketing-pages.md).
5. Run the audit on each state, in light and dark, with and without reduced motion, and with `--marketing` on
   marketing pages ([references/measurement.md](references/measurement.md)). Fix every `fail`; fix or justify every `warn`.
6. Run the `browser-verification` measurement for contrast, overflow, target size and fit on the same states.
7. Review for tells with [references/tells.md](references/tells.md) and remove one decoration.
8. Report: reference and new element screenshots side by side, audit numbers against thresholds, the outside
   references and the value compared against each, kept tells with reasons, and what was not verified.

## Traps

- Designs rejected in a row (generic, then invented, then another surface's style) until built from the same
  surface's existing artifact. Banning one generated look only moves output to the next one.
- A brand colour used as text on white measured 1.7:1 and looked bold and on brand. Premium sites miss contrast
  too, in placeholders, chart axes and mock-ups: copy their restraint, not their values.
- One mark encoding one value in two status colours read as broken; a card holding only a bare table looked
  unfinished next to cards with a visual anchor.
- An empty state repeated the header's "New invoice" button. One state, one call to action.
- Borders defined through the caption colour lightened with every contrast fix to the caption.
- A global focus ring outside `@layer` beat every focus utility; the fix was hunted in specificity.
- A confirm opened from a slideover rendered underneath it, because each overlay picked its own z-index.
- An emoji written into a success message, a README or a seed record ships as authored content; only user input
  may carry emoji.

## Done when

- The reference artifact is named, and its element screenshot sits next to the new one at the same viewport and
  theme.
- For a new surface, the plan names two or three outside references for its surface type, and the review
  compares at least one measured value against them.
- `design_audit.mjs` reports no `fail` against the token list in light and dark, and every `warn` is fixed or
  has a written reason.
- The `browser-verification` measurement passes for contrast, overflow, targets and fit on every state.
- Every state of each changed data view has a fixture and an element screenshot.
- Every number and logo on a marketing page has a claims entry with source and date.
- No `emoji-glyph` or `symbol-icon` finding, no emoji in the changed files outside user-content fixtures, and no
  `unlayered-css` finding without a written reason.
- Every interactive control type has a filled state matrix and element screenshots per state in both themes.
- Every overlay chain the change opens passes the topmost, Escape and focus-return test.

## References

- [references/tokens.md](references/tokens.md): load when extracting or writing tokens, choosing a type or
  spacing scale, or calibrating against measured product sites.
- [references/design-references.md](references/design-references.md): load before designing a new surface, to
  pick the outside references for its surface type and see what each company publishes.
- [references/tells.md](references/tells.md): load when reviewing a design for a generic look or when the audit
  reports tell warnings.
- [references/app-ui.md](references/app-ui.md): load when building or reviewing tables, forms, interactive states,
  icons, overlays, command palettes, shortcuts, charts or dark mode, or when a utility class has no effect.
- [references/marketing-pages.md](references/marketing-pages.md): load when building a landing, pricing or
  feature page, a hero, a product mock-up, or a claims file.
- [references/measurement.md](references/measurement.md): load before running the audit, when reading its
  output, or when Playwright is not installed and the procedure has to run by hand.
- [scripts/design_audit.mjs](scripts/design_audit.mjs): run from the project directory with `--url`, `--tokens`,
  `--scheme dark`, `--reduced-motion`; `--self-test` proves the checks.

## Sources

Each rule names its source inline. Collected:

- https://www.w3.org/TR/WCAG22/ and the Understanding pages for contrast, target size and character key
  shortcuts; https://www.w3.org/WAI/ARIA/apg/ (tooltip, combobox, dialog); all verified 2026-11-01 to 2026-11-06.
- https://github.com/vercel-labs/web-interface-guidelines; https://vercel.com/geist (typography, colors,
  materials); https://linear.app/now/how-we-redesigned-the-linear-ui and
  https://linear.app/now/behind-the-latest-design-refresh; verified 2026-11-01.
- https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md and
  https://www.claude.com/blog/improving-frontend-design-through-skills: generated-design clusters, verified
  2026-11-01.
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/title and
  https://developer.mozilla.org/en-US/docs/Web/CSS/@layer; https://tailwindcss.com/docs/adding-custom-styles;
  verified 2026-11-01 and 2026-11-05.
- https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers, verified
  2026-11-01.
- https://www.unicode.org/reports/tr51/ and https://bugzilla.mozilla.org/show_bug.cgi?id=1970980, verified
  2026-11-05.
- Outside references per surface: URLs in references/design-references.md, verified 2026-11-03.
