# Plural forms per language and framework

## Contents

- Categories per language
- Test counts
- vue-i18n
- i18next
- ICU MessageFormat
- Laravel
- Go
- German examples

## Categories per language

Cardinal categories from CLDR, cross-checked on 2026-11-04 with `Intl.PluralRules` on ICU 77.1 (CLDR 47). "Whole
numbers" lists the categories that integer counts reach; the rest are for fractions or very large numbers.

| Language | CLDR categories | Whole numbers | Note |
|---|---|---|---|
| de, en, nl, da, sv, nb, fi, et, hu, el, bg, tr | one, other | one, other | 0 is `other`: "0 Server" |
| fr, pt | one, many, other | one, other, many | 0 is `one`: "0 serveur"; `many` from 1,000,000 |
| es, it | one, many, other | one, other, many | `many` from 1,000,000 |
| pl, ru, uk | one, few, many, other | one, few, many | `other` only for fractions; ru and uk: 21 is `one` |
| cs, sk | one, few, many, other | one, few, other | `many` only for fractions |
| hr | one, few, other | one, few, other | 21 is `one` |
| ro | one, few, other | one, few, other | 0 and 2..19 are `few` |
| sl | one, two, few, other | one, two, few, other | 101 is `one`, 102 is `two` |
| lt | one, few, many, other | one, few, other | `many` only for fractions |
| lv | zero, one, other | zero, one, other | 10..20 are `zero` |
| ga, mt | one, two, few, many, other | all five | |
| ar | zero, one, two, few, many, other | all six | 100 is `other` |
| ja | other | other | one form |

Source: https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html (verified 2026-11-04).
For a language not in this table, read the CLDR chart or run `new Intl.PluralRules(locale).resolvedOptions()
.pluralCategories` in a current runtime.

## Test counts

Render each counted message for 0, 1, 2, 5, 22 and 101 in every shipped locale, plus 1.5 where fractions occur
(durations, amounts). 22 catches the Slavic `few` after 20, 101 the `one` after 100 in Slovenian and Russian.

## vue-i18n

- Forms are separated by `|`; the count is passed as the second argument or as `{count}` / `{n}`.
- vue-i18n 11.4.18 (`@intlify/core-base`, `pluralDefault`): with two forms, 1 selects the first and everything
  else the second, so 0 takes the plural form; with three or more forms the index is `min(count, 2)`
  (zero | one | other). The rule ignores the locale unless `pluralRules` has an entry for it.
- vue-i18n 12.0.0-alpha.9 adds an automatic rule based on `Intl.PluralRules`. Check the installed major version
  before relying on either behaviour.
- A rule that follows CLDR for every locale, verified for de, fr and pl on 2026-11-04 (0, 1, 2, 5, 22, 112,
  1,000,000). Forms are written in CLDR order (zero, one, two, few, many, other) for the categories the language
  has; an optional zero text is one extra form in front (de 3, fr 4, pl 5):

```ts
const ORDER = ['zero', 'one', 'two', 'few', 'many', 'other']

export function cldrPluralRule(locale: string) {
  const rules = new Intl.PluralRules(locale)
  const cats = [...rules.resolvedOptions().pluralCategories]
    .sort((a, b) => ORDER.indexOf(a) - ORDER.indexOf(b))
  return (choice: number, choicesLength: number): number => {
    const zeroForm = choicesLength === cats.length + 1
    if (zeroForm && choice === 0) return 0
    const index = cats.indexOf(rules.select(Math.abs(choice))) + (zeroForm ? 1 : 0)
    return Math.min(index, choicesLength - 1)
  }
}
// register per shipped locale: pluralRules: { de: cldrPluralRule('de'), pl: cldrPluralRule('pl') }
```

- With this rule a Polish message lists `one | few | many` (other clamps to many), or `one | few | many | other`,
  or a zero text plus all four.
- Do not put a literal `|` into a message; see `vue-inertia-frontend` for literal interpolation.

Sources: https://vue-i18n.intlify.dev/guide/essentials/pluralization (verified 2026-11-04); package contents of
`@intlify/core-base` 11.4.18 and 12.0.0-alpha.9 from npm (read 2026-11-04).

## i18next

- Plural keys carry a category suffix: `server_one`, `server_other`, and for Polish `server_few`, `server_many`.
  Every category the language reaches with whole numbers needs its key.
- The suffixes follow `Intl.PluralRules`, so the file for each language has different keys; parity checks compare
  the base key. Since i18next v24 a runtime without `Intl.PluralRules` resolves only `_one` and `_other`
  (React Native on Hermes needs a polyfill).
- A `_zero` key is used for a count of 0 in any language, in place of the language's own category, so it is the
  natural place for "Keine Server".

Source: https://www.i18next.com/translation-function/plurals (verified 2026-11-04 through a documentation index
tool, Context7).

## ICU MessageFormat

- `{count, plural, =0 {Keine Server} one {# Server} other {# Server}}`. `other` is required. `=0` is an exact
  match and does not replace a category the language needs.
- Put `select` (for example gender) outside and at most one `plural` inside, with full sentences in each branch.
- A category the language does not have (`few` in German) is never selected.

Source: https://unicode-org.github.io/icu/userguide/format_parse/messages/ (verified 2026-11-04).

## Laravel

- `trans_choice('servers.deleted', $count)` selects a segment of a `|`-separated line. A segment may carry an
  interval: `{0}`, `{1}`, `[2,*]`, `[*,0]`.
- Without intervals, `MessageSelector::getPluralIndex()` picks the segment by its own per-locale table, derived
  from Zend Framework code. Segments it selects (laravel/framework 12.53.0, counted over 0..1100 and 10^6):
  de, en, fr, es, it, pt, nl, da, sv, nb, fi, et, hu, el, bg: 2; pl, ru, uk, cs, sk, hr, lt, lv, ro, ga: 3;
  sl, mt: 4; ar: 6; tr, ja: 1. For ga and tr the number of forms differs from CLDR; for lv the selection differs
  (Laravel puts only 0 in the first segment, CLDR also 10 to 20).
- A missing segment falls back to the first one: `'plik|pliki'` returns "plik" for 5 in Polish.
- A line that mixes interval and plain segments strips the intervals and then picks by index:
  `'{0} Keine Server|Ein Server|:count Server'` returns "Ein Server" for 5. Give every segment an interval, or none.
- The table matches `de` and `de_DE`, not `de-DE`; an unknown locale always gets the first segment.
- `:count` is filled automatically; other placeholders come from the third argument.
- `Str::plural()` uses doctrine/inflector with the English ruleset by default; the inflector ships English,
  Esperanto, French, Italian, Norwegian Bokmal, Portuguese, Spanish and Turkish rulesets, no German or Polish. It
  inflects a word and does not translate.

Sources: https://laravel.com/docs/12.x/localization#pluralization (verified 2026-11-04); laravel/framework 12.53.0
`src/Illuminate/Translation/MessageSelector.php` and `src/Illuminate/Support/Pluralizer.php`, run and read
2026-11-04.

## Go

- `golang.org/x/text/message`: a `Printer` for a language formats `%d` and `%f` with localized separators.
- `golang.org/x/text/feature/plural`: `plural.Selectf` takes cases `zero`, `one`, `two`, `few`, `many`, `other`,
  exact `=x` and `<x`; messages are registered in a catalog per language.
- In a worker that only executes checks, user text does not belong there at all; return codes and parameters to
  the service that renders text.

Sources: https://pkg.go.dev/golang.org/x/text/message, https://pkg.go.dev/golang.org/x/text/feature/plural
(v0.43.0, verified 2026-11-04).

## German examples

| Wrong | Right |
|---|---|
| "1 Server(s) gefunden" | `{count} Server gefunden` with forms `one` and `other` (both "Server"), zero: "Keine Server gefunden" |
| "3 Zertifikat(e) laufen ab" | one: "1 Zertifikat läuft ab", other: "{count} Zertifikate laufen ab" |
| "0 Einträge" | "Noch keine Einträge" |
| `count + ' Tage'` | one: "1 Tag", other: "{count} Tage", formatted with `Intl.NumberFormat` |
| "Datei(en) löschen?" | one: "Datei löschen?", other: "{count} Dateien löschen?" |
| "Vor 3 Std." built by hand | `Intl.RelativeTimeFormat('de').format(-3, 'hour')` gives "vor 3 Stunden" |
