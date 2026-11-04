---
name: localization
description: "Builds every user-facing text for localization from the start, UI and backend feedback alike (validation, API errors, toasts, notifications, mail, exports, PDFs): CLDR plural forms instead of 'Server(s)', one sentence per key with named placeholders, Intl formatting, error codes instead of raw exceptions, recipient locale on queued mail. Use when adding user text, counts or locale files. Not for wording or tone."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Localization

This skill decides how user-facing text is built so it can be translated and reads correctly in every language
the product ships: where text lives, how counts, numbers and dates are rendered, how the backend reports errors
to the frontend, and which locale a mail sent from a queue uses. It covers every surface a user reads: UI, validation
messages, API errors, toasts, notifications, mail, exports and PDFs. How the text should read (register, du or
Sie, native phrasing) belongs to `human-copy`; which term a product uses for a thing belongs to the project
glossary (`glossary`, `docs/GLOSSARY.md`). vue-i18n message syntax and the compile test are in
`vue-inertia-frontend` and `web-architecture`; the error envelope is in `api-contract`; Laravel queue and mail
mechanics are in `laravel-production-runtime`. The failures this prevents: "1 Server(s)", "1 Zertifikat(e)",
"0 items", sentences glued from fragments, an English exception shown to a German user, and a mail sent in the
app default instead of the recipient's language.

## Applies when / does not apply

- Applies: any new or changed text a user can see, in any language count, including one; counts, money, dates,
  times, durations and lists in that text; error, validation and status responses that end up on screen; mails,
  notifications, exports and PDFs, queued or not; locale files and their CI checks.
- Applies also to single-language products: one locale file costs little, and the plural, formatting and error
  rules hold in German alone.
- Does not apply: developer logs, metric names, code identifiers, machine-readable export columns that another
  system imports, and command-line output for operators. Wording and tone of the text itself (`human-copy`).

## Rules

Most important first. Examples use a hosting panel that lists servers and certificates and mails expiry notices.

### Text in code

- [invariant] No user-facing literal in code. Every text a user sees goes through the i18n layer, in the frontend
  (`t()`, `<i18n-t>`) and in the backend (`__()`, `trans_choice()`, translated validation, notification and mail
  views). Developer logs are excepted. Why: a literal cannot be translated, and the second language ships half
  done. Test: `i18n_check.py` reports no `S04` or `S05` for the changed files; a pseudo-locale build shows every
  string that is not wrapped in the pseudo delimiters. Source: Microsoft Globalization, pseudolocalization:
  "Resources that haven't been exposed to localization are readily apparent because they won't be
  pseudo-translated" (https://learn.microsoft.com/en-us/globalization/methodology/pseudolocalization, verified
  2026-11-04).
- [invariant] One complete sentence per key with named placeholders (`{count}`, `:name`). Never build a sentence
  from fragments or by joining translated parts, and never reuse a key in another context because the English
  word matches. Why: word order, grammatical case and gender differ between languages; a translator cannot reorder
  pieces they never see together. Test: `i18n_check.py` reports no `S07`; review the diff for one key used in two
  places with different meaning; in the pseudo-locale, paired delimiters inside one sentence reveal a
  concatenation. Source: ICU User Guide, Formatting Messages, "a message has to be written and
  translated as a single unit" and "translators would not be able to rearrange the pieces"
  (https://unicode-org.github.io/icu/userguide/format_parse/messages/, verified 2026-11-04).

### Counted text

- [invariant] Counted text uses the plural mechanism of the i18n layer with the CLDR plural categories of each
  language. Never "(s)", "(e)", "(en)", "(n)", "/s", never `count + ' items'`, never `n === 1 ? 'Server' :
  'Servers'`. German and English use `one` and `other`; Polish, Russian and Ukrainian need `one`, `few` and `many`
  for whole numbers; Arabic has six categories. Why: "1 Server(s)" reads like a machine, and a two-form message
  cannot be right in Polish ("2 pliki", "5 plików"). Test: `i18n_check.py` reports no `I05`, `I06`, `S01`, `S02`
  or `S03`; a unit test renders each counted message for 0, 1, 2, 5, 22 and 101 in every shipped locale. Source:
  Unicode CLDR language plural rules
  (https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html), MDN Intl.PluralRules,
  `select()` returns one of `zero`, `one`, `two`, `few`, `many`, `other`
  (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules), both
  verified 2026-11-04 and cross-checked against CLDR 47 in ICU 77.1.
- [invariant] The forms in the message match what the framework selects. vue-i18n 11 picks forms by a built-in
  English rule (with two forms, 0 takes the plural form) unless `pluralRules` has an entry for the locale; register
  one for every locale beyond `one`/`other` and for French and Portuguese, where CLDR puts 0 in `one`. Laravel's
  `trans_choice()` selects by its own per-locale table: a line with fewer segments than the locale needs falls back
  to the first segment, a line that mixes `{0}` with plain segments picks the wrong form, and a hyphenated locale
  such as `de-DE` always gets the first segment. Why: forms that exist in the file but are never selected look
  correct in review. Test: render 0, 1, 2, 5 and 22 per locale through the real framework call;
  `i18n_check.py` flags the Laravel cases as `I05` and the missing vue-i18n rule as `I09`. Source:
  `@intlify/core-base` 11.4.18 `pluralDefault` (read from the npm package, 2026-11-04), vue-i18n pluralization
  guide (https://vue-i18n.intlify.dev/guide/essentials/pluralization, verified 2026-11-04); laravel/framework
  12.53.0 `src/Illuminate/Translation/MessageSelector.php`, run 2026-11-04 (`'{0} Keine Server|Ein Server|:count
  Server'` returns "Ein Server" for 5).
- [default] Zero gets its own text where it reads better: "Keine Server" instead of "0 Server", "Noch keine
  Zertifikate" instead of "0 Zertifikate". Use ICU `=0`, a Laravel line with an interval on every segment
  (`{0} Keine Server|{1} Ein Server|[2,*] :count Server`), or a separate key for the empty state. Trade-off: one
  more form per message for translators to write. Deviate only with an ADR that names this trade-off. Source: ICU
  User Guide, explicit `=0` values (URL above); Laravel localization, pluralization with ranges
  (https://laravel.com/docs/12.x/localization#pluralization), both verified 2026-11-04.

### Numbers, money, dates and lists

- [invariant] Numbers, money, dates, times, durations, relative times and lists are formatted through Intl or ICU
  in the user's locale and time zone, with the currency code given explicitly. Never `toFixed()`, `number_format()`
  with fixed separators, string-built dates, or a currency sign glued to a number. Why: 1234.5 EUR is "1.234,50 €"
  in German and "€1,234.50" in English, and a date without a time zone is shown in the server's or the
  browser's zone. Test: render the same invoice for `de-DE` with `Europe/Berlin` and `en-US` with
  `America/New_York` and compare with `Intl` output; grep the diff for `toFixed(`, `number_format(`, `date('d.m.`.
  Source: MDN Intl.NumberFormat, "There is no default value; if the style is "currency", the currency property
  must be provided" (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat/NumberFormat);
  MDN Intl.DateTimeFormat, the `timeZone` default "is the runtime's time zone"
  (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat);
  both verified 2026-11-04.

### Backend to frontend

- [invariant] Errors and status responses carry a stable machine code plus parameters; a localized message, if
  sent, is chosen by the requesting user's locale, never the server's. Validation attribute names are translated.
  A raw exception message never reaches a user. Why: clients branch on the code, the frontend can render its own
  text with the parameters, and exception text is English, unplural and leaks internals. Test: per error code, a
  test asserts the code and parameters, and that the message differs between a `de` and an `en` user; a forced
  exception in production mode shows a generic translated text; `i18n_check.py` reports no `S06`. Source:
  RFC 9457 problem details, stable `type` (https://www.rfc-editor.org/rfc/rfc9457.html, see `api-contract`);
  Laravel validation, custom attributes in `lang/xx/validation.php`
  (https://laravel.com/docs/12.x/validation#specifying-attribute-in-language-files); both verified 2026-11-04.

### Locale resolution and async work

- [invariant] The locale is resolved in one place with one order, used by web, API, queue and scheduled work.
  Default order: the user's saved setting, then `Accept-Language`, then the app default. Why: two orders produce a
  German UI and an English mail for the same person. Test: a user with setting `en` and header `de` gets `en`; an
  anonymous request with `de` gets `de`; no header gets the default. Source: RFC 9110 section 12.5.4, the header
  indicates "the set of natural languages that are preferred" and each weight is "an estimate of the user's
  preference" (https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-language, verified 2026-11-04).
- [invariant] Queued mails, notifications, exports and PDFs carry the recipient's locale explicitly: in Laravel the
  notifiable implements `HasLocalePreference` or the send passes `->locale()`; a job receives the locale as a
  parameter and sets it for the duration of its work. Why: the worker runs with the app default, and the recipient
  is often not the person whose request queued the work. Test: queue a mail for a user with locale `en` from a
  request running in `de`, render it, and assert an English subject; the same for a queued export. Source: Laravel
  mail docs, localizing mailables, the locale is remembered "if the mail is queued", and `HasLocalePreference`
  (https://laravel.com/docs/12.x/mail#localizing-mailables); notifications, `->locale()`
  (https://laravel.com/docs/12.x/notifications#localizing-notifications); both verified 2026-11-04.

### Locale files and tests

- [invariant] Every locale has the same keys and the same placeholder set per key, plural forms for its
  categories, and no empty values, checked in CI. Why: a missing key shows the raw key or the fallback language,
  and a lost placeholder silently drops the count. Test: `python3 ${CLAUDE_SKILL_DIR}/scripts/i18n_check.py` exits
  1 on its own bad fixture (`--self-test`) and 0 on the project; add it to CI next to the compile and usage tests
  from `web-architecture`. Source: reproducible with `i18n_check.py --self-test`.
- [default] Layouts are checked with the longest shipped language and with a pseudo-locale that adds accents,
  lengthens text by 40 % and wraps each string in delimiters. German running about 30 % longer than English is a
  practice figure; Microsoft's pseudolocalization heuristic is 40 %, with single words growing more. Trade-off: one
  more locale build and a screenshot pass per release. Deviate only with an ADR that names this trade-off. Source:
  Microsoft Globalization, pseudolocalization, "lengthen the text by 40%" and delimiters that reveal truncation
  and concatenation (URL above, verified 2026-11-04).
- [default] Each locale's text is written in that language from the situation, with `human-copy` for wording,
  register and du or Sie, and the project glossary for terms; machine translation is a draft, not a release.
  Trade-off: slower than translating key by key. Deviate only with an ADR that names this trade-off. Source:
  `human-copy`, references on German UI text and length (verified there 2026-11-03).

## Procedure

### Fast path

1. Text a user sees? Put it in the locale files, never in code. Logs stay as they are.
2. A number next to a noun? One plural message: vue-i18n `t('servers.count', n)`, Laravel `trans_choice()`, ICU
   `{count, plural, ...}`. Give zero its own text if "0 Server" reads badly.
3. Money, date, duration, list? `Intl` or the framework's formatter, user locale, time zone, currency code.
4. Error to the frontend? Machine code plus parameters; no `$e->getMessage()` on screen.
5. Mail, notification, export, PDF from a queue? Pass the recipient's locale.
6. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/i18n_check.py [dirs]`; fix errors, read warnings.

### Full procedure

1. Gate: does the change add or alter text a user can see, a count, a formatted value, an error response or an
   async message? If none, stop.
2. Find the project's i18n layer, locale list, locale resolution and plural setup (vue-i18n `pluralRules`,
   Laravel lang directory and locale names). If a part is missing, propose it before writing text.
3. Name keys by place and meaning (`certificates.expiry.mail.subject`), one sentence per key, named placeholders.
4. Write counted messages per locale with all categories the language needs (`references/plurals.md`), and a
   zero text where it reads better.
5. Route numbers, money, dates, durations and lists through the formatters with locale and time zone.
6. Map backend errors to codes and parameters; translate validation attributes; render a generic translated text
   for unexpected exceptions (`references/backend-feedback.md`).
7. Pass the recipient locale into queued mail, notifications, exports and PDFs, and test the rendered output.
8. Draft the text with `human-copy` and the glossary; then run `i18n_check.py` and the framework compile test.
9. Check the layout in the longest language and in the pseudo-locale.

## Traps

- vue-i18n 11 selects plural forms by an English rule: "{n} plik | {n} pliki" shows "5 pliki" in Polish, and
  French "0 serveurs" instead of CLDR's "0 serveur". vue-i18n 12 (alpha on 2026-11-04) uses `Intl.PluralRules`
  automatically; check the installed version.
- A Laravel locale named `de-DE` makes `trans_choice()` return the first segment for every count. Use `de` or
  `de_DE`.
- `'{0} Keine Server|Ein Server|:count Server'` in Laravel shows "Ein Server" for 5: once one segment has an
  interval, give every segment one.
- `Str::plural()` inflects English (doctrine/inflector ships no German ruleset) and does not translate.
- A German word that is the same in singular and plural ("1 Server", "5 Server") still needs the plural message:
  Polish or a later product rename will not be.
- Mail views rendered in a queue use the worker's locale unless the locale is passed; tests that send
  synchronously in the test's locale stay green.
- A toast that shows `error.message` from a failed request shows whatever the backend or the browser wrote,
  often English.
- Translating machine-readable CSV column names breaks the import on the other side; translate human reports, keep
  machine exports stable and documented.

## Done when

- No user-facing literal in the changed code; `i18n_check.py` exits 0 and its warnings are fixed or allowed with
  a reason (`i18n-allow: reason`).
- Every counted message renders correctly for 0, 1, 2, 5, 22 and 101 in each locale through the real framework.
- Formatted values come from Intl or the framework formatter with locale, time zone and currency code.
- Error responses carry a code and parameters; no raw exception text reaches a user.
- Queued mail, notifications, exports and PDFs render in the recipient's locale in a test.
- The layout holds in the longest language and the pseudo-locale.

## References

- [references/plurals.md](references/plurals.md): load when writing counted messages or setting up plural
  selection: CLDR categories per language, vue-i18n `pluralRules`, i18next suffixes, ICU, Laravel and Go.
- [references/backend-feedback.md](references/backend-feedback.md): load when designing error and validation
  responses, locale resolution, or locale handling for queued mail, notifications, exports and PDFs.
- [references/checker.md](references/checker.md): load before running `scripts/i18n_check.py` on a project, to
  read its finding codes, options and how to calibrate warnings.
- `scripts/i18n_check.py`: locale-file and source checks; `--self-test` runs its fixtures offline.

## Sources

- https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html: cardinal categories per
  language, verified 2026-11-04 and cross-checked against CLDR 47 through ICU 77.1.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules and its
  `resolvedOptions()` page: categories, `pluralCategories`, verified 2026-11-04.
- https://unicode-org.github.io/icu/userguide/format_parse/messages/: single-unit messages, `other` required,
  select outside and plural inside, verified 2026-11-04.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat/NumberFormat
  and .../DateTimeFormat/DateTimeFormat: currency without default, time zone default, verified 2026-11-04.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat: Baseline
  2025, newly available, verified 2026-11-04.
- https://vue-i18n.intlify.dev/guide/essentials/pluralization: pipe forms, `pluralRules`, verified 2026-11-04;
  `@intlify/core-base` 11.4.18 and 12.0.0-alpha.9 package contents, read 2026-11-04.
- https://laravel.com/docs/12.x/localization, /mail, /notifications, /validation: `trans_choice`, ranges,
  `HasLocalePreference`, `->locale()`, attribute names, verified 2026-11-04 through a documentation index tool
  (Context7); laravel/framework 12.53.0 `MessageSelector.php` and `Pluralizer.php`, read 2026-11-04.
- https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-language: Accept-Language, verified 2026-11-04.
- https://learn.microsoft.com/en-us/globalization/methodology/pseudolocalization: pseudo-translation, 40 %
  heuristic, delimiters, pseudo-locale names, verified 2026-11-04.
- https://pkg.go.dev/golang.org/x/text/message and https://pkg.go.dev/golang.org/x/text/feature/plural:
  localized number verbs, `Selectf` cases, v0.43.0, verified 2026-11-04.
