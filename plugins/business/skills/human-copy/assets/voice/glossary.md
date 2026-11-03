# Glossary: [product name]

One row per term and language. `avoid` holds comma-separated variants the linter flags as GLO01
(`copy_lint.py --glossary docs/voice/glossary.md FILE`). Matching ignores case; a trailing `*` matches any
ending (`Slot*` matches "Slots"). List inflected German forms that a `*` cannot reach as separate variants.
Keep the column order; the linter reads `lang | preferred | avoid | note`.

| lang | preferred | avoid | note |
|---|---|---|---|
| de | [Termin] | [Slot*, Zeitfenster] | [example row: replace with your terms] |
| en | [booking] | [reservation] | [example row: replace with your terms] |
