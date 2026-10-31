# i18n safety

vue-i18n compiles messages. `{`, `}`, `@`, `$` and `|` are syntax: placeholders, linked messages, pluralization.
A literal special character is written as literal interpolation, for example `{'@'}`. Sources:
https://vue-i18n.intlify.dev/guide/essentials/syntax and https://vue-i18n.intlify.dev/guide/migration/breaking
(verified 2026-10-31).

## Message syntax

| You want | Write | Not |
|---|---|---|
| an at sign in text | `Contact us {'@'} support` | `Contact us @ support` |
| literal braces | `{'{'}` and `{'}'}` | `{` `}` |
| a dollar sign | `{'$'}` | `$` |
| an email or code example | a component constant rendered next to the message | the example inside the locale file |

A pipe splits a message into plural forms, so a literal pipe is written as literal interpolation of the pipe
character too. Keep code, JSON and email examples out of locale files entirely. They are where most syntax errors come from.

## The three tests

All three run in CI and block the merge. Each one should be seen red once, for example by adding an unescaped
`@` on a branch.

1. Syntax. Load every locale file and compile every message with the compiler of the installed vue-i18n (look up
   its compile API for your version). Fail on any compile error or warning, and print the file, the key and the
   message.
2. Parity. Flatten each locale to its set of key paths. All locales have the same set. No leaf is empty or only
   whitespace. Print missing keys per locale.
3. Usage. Collect static keys from source: `t('...')`, `$t('...')`, `te('...')`, `<i18n-t keypath="...">`. Each
   resolves in every locale through the same nested path lookup the runtime uses, not a flattened map, so a
   literal key that contains dots and that the runtime cannot reach shows up. Dynamic keys
   (`` t(`status.${s}`) ``) go on an allowlist with a source needle: the allowlist entry names a string that must
   still exist in the source, so the entry dies with the code that needed it.

```ts
// usage-test sketch
const STATIC_KEY = /\b(?:\$?t|te)\(\s*['"]([a-z0-9_.-]+)['"]/gi
const KEYPATH = /<i18n-t[^>]*\bkeypath="([a-z0-9_.-]+)"/gi
const DYNAMIC = [
  { prefix: 'status.', needle: "t(`status.${" }, // remove when the needle disappears
]
```

Parity alone misses a key that is absent from every locale. The usage test catches it.

## Renaming and removing keys

Old HTML and JavaScript stay cached for a while after a deploy and may load the new message files. Keep renamed
or removed keys for one release:

1. Release N adds the new key and keeps the old one, marked for removal (a `_remove_after` list next to the
   locale files works).
2. Release N+1 removes the old key.

A CI check diffs the key set against the previous release tag and fails when a key disappeared without being on
the removal list.

## Locale routing

- Public, cacheable pages carry the locale in the path. Nuxt i18n offers the strategies `no_prefix`,
  `prefix_except_default`, `prefix` and `prefix_and_default` (https://i18n.nuxtjs.org/docs/guide, verified
  2026-10-31). A prefix strategy keeps responses cookie-free.
- Browser-language detection in Nuxt i18n sets a cookie (`i18n_redirected` by default) and redirects on the root
  only by default (`redirectOn: 'root'`), documented for v10.6
  (https://i18n.nuxtjs.org/docs/guide/browser-language-detection, verified 2026-10-31). Make sure that cookie
  is set only on the uncacheable root redirect, or disable detection with `detectBrowserLanguage: false`.
- Every locale route renders `html lang` for its locale and `hreflang` links to the others.
- In the dashboard, the server sends the user's locale, the client initializes vue-i18n from it and updates
  `document.documentElement.lang` on every navigation.
- Dates, numbers and money go through `Intl` with the active locale.

## Traps

- One unescaped `@` crashed a dialog only in the production build, with a minified error that named nothing.
- One `{` made a whole locale file fail to load. The page returned 200 with sections missing.
- A key missing from both locales shipped as a raw dotted key on a public page. Parity was green.
- For a short window after each deploy, cached old pages loaded new message files and showed raw keys for
  renamed entries.
