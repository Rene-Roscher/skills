# i18n_check.py

Python 3.9 or later, standard library only. Run from the project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/i18n_check.py resources lang --counts
python3 ${CLAUDE_SKILL_DIR}/scripts/i18n_check.py --self-test
```

Exit codes: 0 no errors, 1 errors (or warnings with `--strict`, or a failed self-test), 2 usage error or nothing
found. Findings print as `path:line: error|warning CODE message`; the summary goes to stderr.

## What it reads

- Locale files: a directory with `[locale].json` files (`de.json`, `en.json`), or a directory with one
  subdirectory per locale holding `.json` or `.php` files. vue-i18n and i18next JSON, nested or flat, and Laravel
  JSON lang files.
- Laravel PHP array lang files only when `php` is on PATH. They are executed with `php -n` to read the array, so
  run it only on your own code, or pass `--no-php`. Without `php` the summary says "not checked".
- Sources: `.vue`, `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.php`, `.blade.php`, `.go`; tests, fixtures, migrations,
  `vendor`, `node_modules`, build output and generated route files are skipped.

## Finding codes

| Code | Level | Meaning |
|---|---|---|
| I01 | error | locale file does not parse |
| I02 | error | key or whole file missing in a locale |
| I03 | error | key exists in a locale but not in the source locale |
| I04 | error | placeholder set differs from the source locale (`{name}`, `{{name}}`, `:name`) |
| I05 | error or warning | plural forms: too few for the language, ICU without `other`, Laravel interval mix, hyphenated Laravel locale; warnings for categories never selected |
| I06 | error | pseudo-plural in a value: "(s)", "(e)", "(en)", "(n)", "/s" |
| I07 | error | empty value |
| I08 | warning | identical to the source locale, probably untranslated |
| I09 | warning | vue-i18n locale that needs a `pluralRules` entry; silence with `--plural-rules pl,fr` once registered |
| I10 | warning | PHP lang file could not be loaded |
| S01 | warning | count concatenated with a noun or with a translated fragment |
| S02 | warning | hand-written plural (`n === 1 ? 'Server' : 'Servers'`, `Str::plural`, `pluralize`) |
| S03 | warning | pseudo-plural in a string literal or template text |
| S04 | warning | hard-coded text in a Vue template or Blade view, or in a static `placeholder`, `title`, `alt`, `aria-label`, `label` attribute |
| S05 | warning | literal user text in a toast, flash, `abort()` or validation error |
| S06 | warning | raw exception message shown to a user (`$e->getMessage()` into a response, `error.message` into a toast, `http.Error(w, err.Error(), ...)`) |
| S07 | warning | one sentence joined from two translations (`t('a') + name + t('b')`, `__('a') . __('b')`) |

## Calibrating

- The source checks are heuristics. Silence a line that is right as it is with a comment on the same or the
  previous line: `<!-- i18n-allow: product name -->`, `// i18n-allow: example value`, `{{-- i18n-allow: ... --}}`.
  A reason is required.
- Internal admin views that are deliberately one-language go out with `--exclude 'resources/views/admin/*'`
  (glob against the path relative to the scanned root). Write that decision down where the team finds it.
- Untranslated detection (`I08`) ignores values under three words and values that look like URLs, code or
  examples. Brand names and identical technical terms are expected hits; allow them in review rather than in the
  locale file.
- Not checked: whether a key is used in code (see the usage test in `web-architecture`), message compile errors
  (compile with the installed vue-i18n), key reuse across contexts, and wording.
