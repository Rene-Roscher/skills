# App UI

## Contents

- Tables
- Empty, sparse and error states
- Loading
- Forms
- Interactive states and the cascade
- Icons, not characters
- Command palette
- Shortcuts
- Overlays
- Charts and data visualisation
- Dark mode
- Checks per component

Vercel's Web Interface Guidelines (https://github.com/vercel-labs/web-interface-guidelines, verified 2026-11-01)
are the source for most items. The guidelines say that a few of their copy and casing preferences are Vercel's
own brand choices; those are left out here. Examples use an invoicing app.

## Tables

- Compared numbers use tabular numerals (`font-variant-numeric: tabular-nums`).
- Filters, sort, tab and page live in the URL, so share, refresh and Back work. The guidelines: "Persist state in
  the URL" and "Deep-link everything".
- Inside a scroll container, cells that hold chips or long names need fixed table layout, explicit column widths
  and truncation with the full value reachable (title popover, detail view, or copy action). Without it the page
  scrolls sideways. Source: none; design judgment, found with the overflow check.
- Long lists: virtualise or use `content-visibility: auto` (guidelines, "Large lists").
- A card that holds only a bare table looks unfinished next to cards that have a visual anchor. Add information
  from components the product already has (a summary strip, an inline bar behind a value, a status pill). Which
  anchor is a project choice. Source: none; design judgment.
- Row height comes from the spacing scale and is recorded in the project profile. Do not invent a density per
  screen.

## Empty, sparse and error states

- Design all of them: empty, one item, dense, error ("All states designed. Empty, sparse, dense, & error
  states.").
- One state, one call to action. If the page header already has "New invoice", the empty state says what will
  appear here and shows no second button. If only the empty state carries the action, keep it there. Source: none;
  design judgment.
- An error says what happened and how to fix it, does not apologise, and is never vague. The guidelines: "Error
  messages guide the exit" and "No dead ends". The frontend-design skill adds that errors speak in the interface's
  voice rather than a person's.
- Partial states need their own design: some data failed, a figure is stale, a list is cut off. Show what is known
  and mark what is not.

## Loading

- Show a spinner or skeleton only after a short delay (about 150 to 300 ms) and keep it visible for a minimum
  time (about 300 to 500 ms), so fast responses do not flicker.
- Skeletons mirror the final layout exactly, to avoid layout shift.
- A loading button keeps its label and adds an indicator; progress labels end with an ellipsis character
  ("Saving...").

## Forms

From the guidelines:

- Every control has a label, and clicking the label focuses the control.
- Enter submits a form with one control; Cmd or Ctrl plus Enter submits a textarea.
- Do not pre-disable submit: let people submit an incomplete form to see validation. Disable only while the
  request is in flight, and send an idempotency key.
- Show errors next to their fields and focus the first one on submit.
- Set `autocomplete`, `name`, `type` and `inputmode`; never block paste or typing; inputs are at least 16 px on
  mobile to avoid zoom on focus.
- Placeholders show an example value and end with an ellipsis character.
- Warn before navigation that would lose unsaved changes.

## Interactive states and the cascade

Write the state matrix before the first utility class. One row per control type, one column per state, each cell
a token or "same as default":

| Control | Default | Hover | Focus-visible | Active | Disabled | Invalid | Checked or pressed |
|---|---|---|---|---|---|---|---|
| text input | `--input-border`, `--surface` | border one step stronger | ring token, border unchanged | n/a | `--surface-muted`, `--text-muted` | `--danger` border, message below | n/a |
| button, secondary | | | | | | n/a | n/a |
| toggle button | | | | | | n/a | accent surface, `aria-pressed="true"` |

- Decide which states change at all. A quiet input that only changes on focus is a valid design; an input that
  changes border, background, shadow and ring on hover and focus is noise.
- Focus uses `:focus-visible`, so a mouse click does not draw the ring; focus indicators meet 3:1 against adjacent
  colours (WCAG 2.2, 1.4.11 and 2.4.7).
- Hover is never the only cue: touch has no hover.
- Fill the matrix for light and dark.

Cascade: normal declarations outside any `@layer` beat every layered declaration, whatever the specificity
(MDN, "Styles that are not defined in a layer always override styles declared in named and anonymous layers.",
https://developer.mozilla.org/en-US/docs/Web/CSS/@layer, verified 2026-11-05). Tailwind CSS v4 emits its own
layers (`theme`, `base`, `components`, `utilities`), so a global `:focus-visible` or `input` rule written as plain
CSS after `@import "tailwindcss"` wins over every `focus-visible:` utility in the app. Put element defaults and
global rings in `@layer base` and component classes in `@layer components`
(https://tailwindcss.com/docs/adding-custom-styles, verified 2026-11-05). When a utility "does nothing", read the
computed style and the winning rule in the browser before raising specificity; the audit's `unlayered-css`
warning lists the rules that sit outside a layer. Third-party CSS injected without a layer (some toast and date
picker libraries do this) shows up there too: wrap its import in a layer (`@import "lib.css" layer(components)`)
or justify it.

## Icons, not characters

- Icons come from the project's icon set (for example Lucide) or inline SVG: `currentColor`, sized from the type
  scale, `aria-hidden="true"` next to a visible label, an accessible name (`aria-label` on the button) when the
  icon stands alone.
- Flags are SVG assets (a flag icon package or files in the repo), always with the language or country name as
  text; a flag alone does not name a language.
- No emoji and no character drawn as an icon: check marks, crosses, stars, warning signs, arrows on buttons, a
  multiplication sign as the close button, bullets as status dots. The audit fails on `emoji-glyph` and
  `symbol-icon`.
- Exempt: what users wrote (mark the container `data-user-content`) and code samples.
- Windows' emoji font has no flag glyphs and shows the two letters instead
  (https://bugzilla.mozilla.org/show_bug.cgi?id=1970980 comment 6, verified 2026-11-05). Emoji in general come
  from each platform's colour font, ignore the theme and `currentColor`, and differ between systems (Unicode
  Technical Standard 51, section 2.2, https://www.unicode.org/reports/tr51/, verified 2026-11-05).

## Command palette

- Build it as a combobox with a listbox popup. DOM focus stays in the input; the active option is referenced with
  `aria-activedescendant`. Down and Up move, Enter accepts, Escape closes without changing the previous value.
  Source: ARIA APG combobox pattern (https://www.w3.org/WAI/ARIA/apg/patterns/combobox/, verified 2026-11-01):
  "DOM Focus is maintained on the combobox and the assistive technology focus is moved within the listbox using
  aria-activedescendant".
- Commands that open a follow-up step end with an ellipsis character ("Rename...").
- Show the shortcut next to each command, with platform symbols.
- Cmd+K as the opener is a convention, not a requirement.

## Shortcuts

- A shortcut that uses only a letter, digit, punctuation or symbol key can be turned off, remapped to include a
  modifier, or is active only while its component has focus (WCAG 2.2, 2.1.4, Level A). Voice input turns speech
  into letters, so such shortcuts fire by accident.
- Every shortcut also exists as a visible control.
- Let people choose where the choice matters (for example Enter or Ctrl+Enter to send).
- Every drag, swipe or pinch also works with a click or tap and the keyboard.

## Overlays

- Tooltips hold text only. APG: "Tooltip widgets do not receive focus. A hover that contains focusable elements
  can be made using a non-modal dialog." Links, buttons and copy actions go into a popover or hover card that
  opens on hover, focus and click.
- Use the design system's tooltip, not the `title` attribute. MDN: use of `title` is "highly problematic" for
  touch-only devices, keyboard users, and assistive technology users
  (https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/title, verified 2026-11-01).
- Delay the first tooltip in a group; peers open without delay (guidelines).
- One modal at a time. A confirmation that follows a dialog replaces it or follows after it closes; stacked
  overlays compete for focus traps. Source: none; design judgment. Where a confirm has to open from a sheet or
  slideover, it takes the higher step of the stacking scale (tokens reference, "Stacking scale") and is
  portalled to `<body>`; a browser test asserts the confirm is the topmost element at its centre
  (`document.elementFromPoint`).
- Sticky headers, footers and banners never cover the focused element (WCAG 2.2, 2.4.11).

## Charts and data visualisation

- Colour is never the only cue (WCAG 1.4.1): add labels, patterns or direct annotation. Lines, bars and focus
  rings are at least 3:1 against adjacent colours (WCAG 1.4.11). Use a colour-blind-friendly palette.
- One mark encodes one value. A bar for a booking slot that is partly full is one bar in one status colour filled
  by share, not a bar with a red base and a green rest, which reads as broken. Source: none; design judgment.
- Overviews of many items (hundreds of failing payments, for instance) lead with the grouping event: title, count
  and a link; then a capped list with "+N more" and totals; every item in a detail popover links to its page. Test
  with the worst realistic count, not three sample rows.
- Axis labels and legends are text and follow the 4.5:1 rule; they are where grey tends to go wrong.

## Dark mode

- Set `color-scheme: dark` on `html` in dark themes and a matching `theme-color`; set `background-color` and
  `color` on native `select` elements (guidelines).
- Re-run every contrast check in both themes; a grey that passes in light often fails in dark.
- Derive themes from few inputs and re-check each output rather than hand-tuning many variables.
- Interaction states (hover, active, focus) have more contrast than the rest state.

## Checks per component

| Component | Check | How |
|---|---|---|
| table | numeric cells compute `tabular-nums` | audit `tabular-nums` warning |
| table in a container | no horizontal overflow with a 200-character name | audit `overflow`, fixture with a long name |
| any data view | one fixture and screenshot per state | review |
| form | first error focused; submit enabled before the request | browser test through `browser-verification` |
| command palette | `role=combobox` input, `aria-activedescendant` changes on Down | browser test |
| tooltip | no focusable element inside the tooltip component | lint over component files |
| icons | no emoji, no character as icon, flags as SVG | audit `emoji-glyph`, `symbol-icon` |
| interactive controls | state matrix filled for both themes; every state has an element screenshot | review and browser test |
| global CSS | no rule outside `@layer` on a layered page | audit `unlayered-css` |
| overlays | no numeric `z-index` outside the scale; a confirm from a sheet sits on top | audit `off-token-zIndex` with `zIndex` tokens, browser test |
| shortcuts | with the setting off, the key does nothing in the page body | browser test |
| chart | every series has a second cue; marks at least 3:1 | review and contrast measurement |
| dark mode | audit with `--scheme dark` shows no new `contrast` fail | audit |
