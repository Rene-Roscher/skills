---
name: human-copy
description: "Writes and reviews website, product, changelog, release-note, mail, docs and README text in English and German so it reads as written by a person for one reader: sourced claims or none, no unproven superlatives, no generic AI cadence, native German instead of translated English. Use when drafting or editing such copy, or when text sounds machine-made. Not for commit messages, positioning, code comments or legal translation."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Human copy

This skill decides what a piece of public text may claim and how it is built, in English and German. The goal is
copy a specific person could have written for a specific reader: every claim has a source or is not written, the
first sentence says what the thing does, and the German is written in German, not translated. The defect it
targets is generic content, not vocabulary. A text that swaps flagged words for synonyms but still fits any
competitor is still bad copy. It does not decide positioning, pricing or visual design.

## Applies when / does not apply

- Applies: you draft or edit a landing page, feature page, changelog, release notes, product mail, docs page,
  README intro or social post in English or German; you review a draft that sounds generic, inflated or
  machine-made; you localise copy into German; you check a draft for unsourced superlatives, invented numbers or
  testimonials.
- Does not apply: commit messages and pull request text (`commit-hygiene`), who the product is for and how it is
  positioned (`product-strategy`), prices and plan limits (`pricing-and-unit-economics`), code comments, and
  translating legal or contract text, where the legal wording rules.

## Rules

- [invariant] Every number, comparison, customer name, logo, quote, rating, award and "first" or "only" claim in
  copy traces to a source you have seen: a measurement, a link, a dated record, a consent. Without one the claim
  is not written; put `{TODO: source}` in the draft and name the gap in your report. Never invent a figure, a
  customer or a person to make a sentence concrete. Why: fabricated testimonials and figures are the most
  expensive error in copy, and a number in a sentence reads as proof whether or not it is. Test: given a draft
  that says "trusted by 10,000 teams" and a facts file without a customer count, the result drops the claim or
  carries `{TODO: source}`, and the report lists it. Source: https://www.ecfr.gov/current/title-16/part-465
  (US, fake or misrepresented reviews and testimonials, section 465.2) and
  https://www.gesetze-im-internet.de/uwg_2004/anhang.html (DE, Nr. 23b and 23c, consumer-facing) (verified
  2026-11-01). Review-ready draft, not legal advice.
- [invariant] A superlative, "only", "first" or "leading" claim carries its basis in the same sentence: compared
  with what, measured how, when, with a link. Otherwise rewrite it to the verifiable fact. Why: an unprovable
  "best" or "fastest" is both an empty claim to the reader and a misleading-claim risk. Test: "the fastest status
  page" with no benchmark becomes either a sentence with the benchmark and its date or the measured value alone
  ("checks every 30 seconds"). Source: https://www.gesetze-im-internet.de/uwg_2004/__5.html (DE, section 5:
  misleading statements about advantages apply to consumers and other market participants) and
  https://www.gesetze-im-internet.de/uwg_2004/__6.html (DE, section 6: comparative advertising must relate
  objectively to verifiable features) (verified 2026-11-01). Details and jurisdiction notes:
  [references/claims.md](references/claims.md).
- [invariant] Copy describes what ships today. A benefit that is planned, in design or only partly built is
  either left out or stated as the basis for later work without a date. Why: readers act on the page, and a
  described benefit the product does not deliver is a false statement about its features. Test: a draft says
  the tool "automatically recovers failed payments" while the facts say only the failure is logged; the result
  states the logging and nothing more. Source: https://www.gesetze-im-internet.de/uwg_2004/__5.html (verified
  2026-11-01), section 5(2) Nr. 1 lists availability, advantages and expected results.
- [invariant] No chat residue, placeholder or unfilled template ships: greetings, "here is a revised version",
  offers to help, `[Company]`, `{TODO}`, "lorem ipsum". Why: they show nobody read the text before publishing.
  Test: a draft that opens with "Of course! Here is the updated page:" has that line removed, and
  `copy_lint.py` reports no RES01 on the result. Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
  (collaborative communication and placeholder text, verified 2026-11-01).
- [invariant] German copy uses German typography and German grammar: quotes „so“ or »so«, no English title case
  in headings, decimal comma and thousands point, "19 €" not "€19", no apostrophe before genitive -s, compounds
  joined or hyphenated. Why: these are orthography and localisation norms, so a violation is an error whoever
  wrote the text. Test: "Die "Status Seite" zeigt Kunden's Störungen, €19" is flagged TYP01, TYP02, TYP03 and
  TYP05 by `copy_lint.py --lang de`. Source: https://aka.ms/german-styleguide
  (capitalisation, quotes, number format) and https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf
  (§ 53 headings) (verified 2026-11-01).
- [default] Test every sentence for substitution: put a competitor's name in place of the product's. If the
  sentence is still true, rewrite it with something only you can say: a number with unit and baseline, a
  mechanism, a limit, a named integration, a policy. Comparative and benefit verbs (faster, fewer, saves,
  reduces) get a number and a baseline or a "because". Trade-off: some sentences have no specific fact behind
  them, so they are cut and the page gets shorter. Deviate only with an ADR that names this trade-off. Source:
  https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (generic statements that fit many topics),
  https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ (verified 2026-11-01).
- [default] Fix substance before surface. Collect the facts, write the one-line job of the text, draft plain, then
  run the linter. Treat a tell-word or pattern hit as a prompt to find the fact behind the sentence, not as a
  verdict on authorship and not as a score to drive to zero. Do not swap a flagged word for a synonym. Trade-off:
  slower than a word swap, and some hits stay with a written reason. Deviate only with an ADR that names this
  trade-off. Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing ("this list is descriptive,
  not prescriptive"; treating the signs alone "could just make detection harder"; a word overused by AI does
  not imply its synonyms are) (verified 2026-11-01).
- [default] Open with what the thing does and for whom; end on the last useful fact or the next action. No
  scene-setting opener, no rhetorical question, no summary closer, no importance flag. Keep sentences at or
  under 25 words. Trade-off: less warm-up, so brand voice must come from precision rather than flourish.
  Deviate only with an ADR that names this trade-off. Source: https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice
  (get to the point fast, front-load) and
  https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style (25 words) (verified 2026-11-01).
- [default] Treat contrast, triads, em dashes and participle tails as density signals, not bans. At most one
  "not X but Y" per page and none in a headline, subject line or first sentence; a triad only when each item is
  concrete, distinct and true; en dash rules per language (see the references); no sentence-final participle
  that only comments. Trade-off: some of these are good human style, so a flagged sentence can stay when the
  claim behind it is specific. Deviate only with an ADR that names this trade-off. Source:
  https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (negative parallelisms are common in human
  writing; rule of three; the em-dash indicator is listed as historical for 2022 to September 2026)
  (verified 2026-11-01).
- [default] Keep tell lists dated and local. A list of flagged words or phrases is a snapshot: it carries a
  last-reviewed date, it is re-checked when models change, and domain words (such as "reliable" for a monitoring
  tool) are judged by the claim around them, not by the word. Trade-off: maintenance, and a stale list gives
  false comfort. Deviate only with an ADR that names this trade-off. Source:
  https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (words and eras; em dashes moved to historical
  indicators) (verified 2026-11-01). The lists of this skill live in `scripts/copy_lint.py`, last reviewed 2026-11-01.
- [default] One surface, one register. Docs, incident and status notices, legal pages and error messages carry no
  marketing words, no exclamation marks and no "please" padding. Marketing pages use at most one exclamation
  mark. Chat tone does not leak into any of them. Trade-off: docs read plainer than the brand voice elsewhere.
  Deviate only with an ADR that names this trade-off. Source: https://developers.google.com/style/tone (avoid
  exclamation points; politeness without overusing "please") and
  https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style ("no need to say please") (verified 2026-11-01).
- [default] One term per concept, one address form per product, brand names as the brand writes them. German: pick
  du or Sie for the whole product (UI, mail, docs) and keep it; "du" and "dein" are lowercase outside letters,
  "Sie" and "Ihr" always capital. Trade-off: statutory text may need the formal form, which then stays isolated.
  Deviate only with an ADR that names this trade-off. Source: https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf
  (§ 65 Sie capitalised, § 66 du lowercase, capital allowed in letters) (verified 2026-11-01).
- [default] German is written from the German fact, not translated from an English draft. Prefer a verb over a
  noun chain, active over passive, a main clause first, "wir" and "du" over "man" and "seitens". English terms
  stay only when they are the target group's standard word or a UI label, inflected by German grammar. Trade-off:
  more rewriting than a literal translation. Deviate only with an ADR that names this trade-off. Source:
  https://mik.brandenburg.de/sixcms/media.php/9/BuergernaheSpracheinderVerwaltung.pdf (verbs instead of nouns,
  active instead of passive, at most four nouns in a row) and the Microsoft German style guide above (anglicisms
  only when industry standard; indicative and imperative instead of subjunctive) (verified 2026-11-01).
- [default] A changelog or release note says what changed, for whom and how to use it, in groups (Added, Changed,
  Deprecated, Removed, Fixed, Security), newest first, with ISO dates. It lists customer-facing changes only and
  never a pasted commit log. Trade-off: internal work stays invisible. Deviate only with an ADR that names this
  trade-off. Source: https://keepachangelog.com/en/1.1.0/ (verified 2026-11-01).
- [default] Read the final text aloud. Rewrite any sentence you would not say to the reader. Trade-off: a few
  minutes per page. Deviate only with an ADR that names this trade-off. Source:
  https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice (verified 2026-11-01).

## Procedure

1. Name the surface (landing, feature page, changelog, mail, docs, README), the language, the reader and the one
   job of the text: "This text makes [reader] do [action] because [fact]." If you cannot fill it, ask.
2. Collect facts before writing: behaviour, limits, real numbers with source and date, real UI labels, the
   reader's own words (support tickets, search queries). Write them in a short list. Anything outside the list
   is a claim that needs a source; read [references/claims.md](references/claims.md) for how to source it.
3. Draft plain: is/has/uses, verbs first, digits, sentence case, no decoration. In German read
   [references/de.md](references/de.md) first; in English read [references/en.md](references/en.md).
4. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/copy_lint.py --lang auto FILE`. In clients that do not set
   `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder. Fix every SUP01, RES01, DSH02 and
   language-specific TYP finding; read the rest as prompts.
5. Substitution test and claim pass: each sentence that survives a competitor swap gets a fact or is cut; each
   superlative, number, customer and quote gets its source or `{TODO: source}`.
6. Rebuild structure for the surface: no contrast headline, triad or participle tail without a fact behind it; headings
   only where a reader navigates; markdown only where it renders.
7. Read aloud, then run the linter again and compare. Keep a remaining hit only with a one-line reason.
8. Report: what was removed or marked `{TODO: source}`, which findings remain and why, and which facts the writer
   still needs from a human.

## Traps

- Replacing a flagged word with a synonym. The empty claim is the tell, not the word.
- Making a sentence concrete with an invented number, customer or quote.
- Driving the linter to zero. It is calibrated and warns; a hit on a precise changelog line can stay.
- Telling an author the text "is AI". No single marker proves it; criticise the claim, not the origin.
- Translating an English draft into German and calling it localised.
- Mixing du and Sie because a statutory template was pasted in.
- Keeping a "not X but Y" headline because it sounds punchy.
- Applying marketing tone to docs, status updates or error text.
- Judging a domain word by the word alone ("reliable" for a monitoring tool) instead of the claim around it.

## Done when

- Every number, comparison, superlative, customer, logo, quote and award has a source or `{TODO: source}`, and the
  report names each gap.
- The text describes only what ships today.
- No chat residue, placeholder or unfilled template remains.
- Each sentence fails the substitution test or was cut; the first sentence says what the thing does.
- German text uses one address form, German quotes, German number format and sentence-case headings.
- `copy_lint.py` was run before and after; remaining hits carry a one-line reason.
- The text was read aloud.

## References

- [references/en.md](references/en.md): read when writing or reviewing English copy; patterns, calibrated markers,
  rewrite examples and genre notes.
- [references/de.md](references/de.md): read when writing or reviewing German copy; typography, calques, address
  form, nominal style, examples and genre notes.
- [references/claims.md](references/claims.md): read when a draft contains a number, comparison, superlative,
  customer, testimonial or award, or when someone asks what the law says about it.
- `scripts/copy_lint.py`: run on every draft; `--help` lists the options, `--self-test` checks the script itself.

## Sources

- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing: field guide to AI writing signs by era; descriptive,
  not prescriptive; generic content as the core problem; humans are poor detectors; the em-dash indicator moved
  to historical (verified 2026-11-01).
- https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/: in a five-style web
  writing test the objective version scored 27 % higher on measured usability than the promotional control, the
  concise one 58 %, the combined one 124 % (verified 2026-11-01).
- https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice: front-load, write like you speak, read aloud,
  sentence-style capitalisation (verified 2026-11-01).
- https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style: 25-word sentences, sentence case, bold only for
  interface elements, words to avoid (verified 2026-11-01).
- https://developers.google.com/style/tone: avoid exclamation points; do not over-use "please" (verified 2026-11-01).
- https://keepachangelog.com/en/1.1.0/: changelogs are for humans; change types; newest first (verified 2026-11-01).
- https://www.gesetze-im-internet.de/uwg_2004/__5.html, /__6.html, /anhang.html: German UWG sections 5 and 6 and
  the annex (verified 2026-11-01).
- https://www.ecfr.gov/current/title-16/part-465: US rule on consumer reviews and testimonials; text read through
  the eCFR renderer API (verified 2026-11-01).
- https://aka.ms/german-styleguide: German
  localisation style (verified 2026-11-01).
- https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf: German orthography 2024, sections 53, 65, 66
  (verified 2026-11-01).
- https://mik.brandenburg.de/sixcms/media.php/9/BuergernaheSpracheinderVerwaltung.pdf: plain-language guide of a
  German interior ministry (verified 2026-11-01).
