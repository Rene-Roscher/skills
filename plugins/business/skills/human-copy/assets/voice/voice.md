# Voice: [product name]

Copy this file to `docs/voice/voice.md` in the product repository (or the path your project facts name) and
fill every line. Delete a line only when the product has no such surface. Anything left in square brackets is
undecided, and the writing skill treats it as undecided.

Owner: [role of the person who approves copy] · Last reviewed: [YYYY-MM-DD]

## Reader

- Who reads it: [for example "owners of small trades businesses who send 10 to 50 invoices a month"]
- What they already know: [terms they use themselves, terms they do not know]
- Languages: [de, en]; source language for new copy: [de or en, or "both written separately"]

## Address form

- German: [du or Sie] in product UI, mails, website, docs and support.
- Capitalisation: [du/dein lowercase (standard)] or [Du/Dein capitalised, letters and mails only]
- Legal texts (AGB, Datenschutz, AVV): [Sie or neutral third person ("der Kunde")], kept on their own pages.
- Exceptions by audience, each with its ADR: [none] or [for example "tax advisors: Sie, ADR-007"]
- English: [you; "we" for the company or not at all]

## Tone per surface

| Surface | Tone in one line | Sentence length | Allowed | Not allowed |
|---|---|---|---|---|
| UI labels and buttons | [plain, verb first] | [1 to 4 words] | | |
| Error messages | [calm, what happened and what to do] | [up to 2 short sentences] | | |
| Empty states | [what goes here, one next step] | | | |
| Transactional mail | | | | |
| Incident or status notices | [facts, times with zone, next update] | | | |
| Docs | | | | |
| Marketing and website | | | | |
| Changelog | | | | |
| Legal | [precise, formal] | | | |

## House choices

- Numbers: [1.000 (point) or 1 000 (space) for counts]; money: [19 €, 1.234,50 €]
- Dates and times: [03.11.2026 or 3. November 2026]; [14:30 Uhr]; time zone shown as [MEZ/MESZ or UTC]
- Gender approach: [neutral nouns and plurals first, no gender sign] or [named alternative]
- Product's own words for its concepts: see `glossary.md`
- English variant: [US or UK spelling]
- Quotes: [„…“ or »…«]; dash: [spaced en dash or none]

## Words we do not use, and why

Keep this list short. Long ban lists belong in `glossary.md`, which the linter reads after drafting, not in
the text an agent reads before drafting.
