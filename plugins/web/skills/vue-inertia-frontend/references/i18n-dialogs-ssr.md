# Locale messages, dialogs and SSR

## vue-i18n message syntax

Reserved characters in messages: `{` `}` `@` `$` `|`. Literal interpolation writes them as text:

```json
{
  "support": {
    "contact": "Write to support{'@'}example.com",
    "price": "From {amount} per month",
    "choice": "no items | one item | {count} items"
  }
}
```

- `@:key` and `@.modifier:key` are linked messages; any other `@` is an error.
- `|` separates plural forms. A literal pipe needs `{'|'}`.
- Code samples, JSON payloads and template syntax do not belong in locale files. Keep them as constants in the
  component and translate only the prose around them.
- Failure shape seen in practice: a broken message throws during render, so the component that uses it (often a
  dialog or a select) breaks while the rest of the page works; a broken message in a lazily loaded file made the
  whole file fail to load, and unrelated keys from it showed up as missing.

Guard test, run in CI over every locale file:
1. Compile each message with the same compiler the app uses, or reject unescaped `@` (not followed by `:` or `.`)
   and unbalanced `{` `}` by pattern.
2. Assert all locales have the same key set with no empty values.
3. Extract static `t('...')` keys from the source and assert each resolves in every locale.

## Dialogs

- Title: `DialogTitle` (visible) gives the accessible name. A dialog without a visible title gets an
  `aria-label`.
- Description: render `DialogDescription` when there is one; do not set `aria-describedby` yourself, and never to
  `undefined` while a description is rendered.
- Without `DialogTrigger`, the primitive may not generate a content id; pass one (`useId()`).
- Focus: moves into the dialog on open (first focusable element, or the dialog itself when the first element is a
  destructive action), returns to the trigger on close.
- Confirmation dialogs take plain text plus the substrings to emphasize, not HTML.
- One overlay at a time: when several one-time dialogs or tours can open on the same screen, route them through one
  coordinator with a fixed priority, and release the slot when an overlay decides not to show.

## Dialogs during SSR or hydration

Inertia dashboards usually render on the client. These apply when a dialog is open in the server render, for
example a URL that opens a detail modal on an SSR page.

- Portals render on the server only when force-mounted; teleport into the target the SSR framework renders (for
  Nuxt, its teleports container).
- Scroll lock and the dismissable layer both write `pointer-events` on `<body>`. A dialog open at hydration could
  leave `pointer-events: none` after closing on Reka UI versions before the fix for issue 2867
  (https://github.com/unovue/reka-ui/issues/2867). On those versions, clear the body style on unmount when no
  dismissable layer remains in the DOM, or mount the overlay only after hydration. Check the installed version.
- Teleported content hangs under `<body>`: set the text color and `color-scheme` there, not only on a layout
  wrapper, or dark mode shows dark text on a dark background.
- Prove the closed state in a browser test: after closing, a click on a page button still works.
