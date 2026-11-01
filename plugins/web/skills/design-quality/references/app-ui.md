# App UI

## Contents

- Tables
- Empty, sparse and error states
- Loading
- Forms
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
  overlays compete for focus traps. Source: none; design judgment.
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
| shortcuts | with the setting off, the key does nothing in the page body | browser test |
| chart | every series has a second cue; marks at least 3:1 | review and contrast measurement |
| dark mode | audit with `--scheme dark` shows no new `contrast` fail | audit |
