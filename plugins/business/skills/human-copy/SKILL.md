---
name: human-copy
description: "Writes and reviews English and German product text (UI, mail, website, docs, changelog) so it reads native: sourced claims, register per surface, a native rewrite pass, corpus-checked collocations, the product's voice files and owner corrections. Use when drafting or editing such copy or when it reads machine-made or translated. Not for commits, positioning, code comments or legal translation."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Human copy

This skill decides what a piece of product text may claim, which register it uses, and how it gets from a
draft to text a native writer would have produced, in English and German. It covers two layers. The first is
claims and obvious machine cadence: every claim has a source or is not written. The second is text that is
correct and still reads off: a noun where a person would use a verb, a word combination no native writer uses,
a brochure tone in an error message, a product term that changes from screen to screen. The second layer is
fixed by the product's own evidence (approved texts and the owner's corrections), a separate native pass and a
corpus check, not by a longer list of banned words. It does not decide positioning, pricing or visual design.

## Applies when / does not apply

- Applies: you draft or edit UI strings, error messages, empty states, confirmations, settings text, toasts,
  transactional mail, incident or status notices, landing and feature pages, changelogs, release notes, docs,
  README intros or social posts in English or German; a draft sounds generic, inflated, translated or
  machine-made; the owner corrects your wording; you localise copy into German.
- Does not apply: commit messages and pull request text (`commit-hygiene`), who the product is for and how it
  is positioned (`product-strategy`), prices and plan limits (`pricing-and-unit-economics`), code comments, and
  translating legal or contract text, where the legal wording rules.

## Rules

Examples come from an invoicing app, a booking system and a project tool.

### Claims

- [invariant] Every number, comparison, customer name, logo, quote, rating, award and "first" or "only" claim
  traces to a source you have seen: a measurement, a link, a dated record, a consent. Without one the claim is
  not written; put `{TODO: source}` in the draft and name the gap in your report. Never invent a figure, a
  customer or a person to make a sentence concrete. Why: a number in a sentence reads as proof whether or not
  it is, and fabricated testimonials are the most expensive error in copy. Test: a draft says "trusted by
  10,000 teams" and the facts have no customer count; the result drops the claim or carries `{TODO: source}`,
  and the report lists it. Source: https://www.ecfr.gov/current/title-16/part-465 (US, section 465.2) and
  https://www.gesetze-im-internet.de/uwg_2004/anhang.html (DE, Nr. 23b and 23c) (verified 2026-11-01).
  Review-ready draft, not legal advice.
- [invariant] A superlative, "only", "first" or "leading" claim carries its basis in the same sentence:
  compared with what, measured how, when, with a link. Otherwise it becomes the verifiable fact. Why: an
  unprovable "fastest" is empty to the reader and a misleading-claim risk. Test: "the fastest invoicing tool"
  with no benchmark becomes a sentence with the benchmark and its date, or the measured value alone. Source:
  https://www.gesetze-im-internet.de/uwg_2004/__5.html and https://www.gesetze-im-internet.de/uwg_2004/__6.html
  (verified 2026-11-01). Details: [references/claims.md](references/claims.md).
- [invariant] Copy describes what ships today. A planned or partly built benefit is left out. Why: readers act
  on the page. Test: the draft says the tool "automatically recovers failed payments" while the facts say only
  that the failure is logged; the result states the logging and nothing more. Source:
  https://www.gesetze-im-internet.de/uwg_2004/__5.html, section 5(2) Nr. 1 (verified 2026-11-01).
- [invariant] No chat residue, placeholder or unfilled template ships: greetings, "here is a revised version",
  offers to help, `[Company]`, `{TODO}`, "lorem ipsum". Why: they show nobody read the text before publishing.
  Test: a draft that opens with "Of course! Here is the updated page:" loses that line, and `copy_lint.py`
  reports no RES01. Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (verified 2026-11-01).
- [invariant] The writer adds no Unicode emoji or pictographic symbol (check marks, stars, flags, arrows as
  bullets) to any text, wherever it sits in a line; a visual cue is an icon from the product's set or an SVG,
  placed by the component, not by the copy. Quoted user content keeps what the user typed. Why: emoji render
  differently on every platform and read as filler. Test: a draft with a rocket in a heading and a check mark in a
  list item yields two EMO01 findings from `copy_lint.py`. Source: none; design judgment.

### Voice and learning

- [default] Read the product's voice files before drafting: `voice.md`, the glossary, the corrections for the
  same surface and language, and the approved examples. Default location `docs/voice/`, or the path the
  project facts name. If they do not exist, offer to create them from [assets/voice/](assets/voice/voice.md)
  and continue with this skill's defaults. Trade-off: a few files to keep current, in exchange for drafts that
  start from the owner's choices instead of the model's. Deviate only with an ADR that names this trade-off.
  Source: https://github.com/anthropics/knowledge-work-plugins/tree/main/partner-built/brand-voice (a guidelines
  file read before writing) and https://arxiv.org/abs/2404.15269 (preferences learned from user edits)
  (verified 2026-11-03). Format and loop: [references/voice-files.md](references/voice-files.md).
- [invariant] Few-shot only from real approved texts. Before drafting, load 3 to 5 approved, shipped texts of
  the same surface and language. If none exist, say so in the report and mark the draft "unreviewed voice".
  Never write an example and present it as approved, and never claim the draft matches a house voice you had
  no texts for. Why: examples steer tone more reliably than descriptions, so an invented example steers toward
  the model's own default and hides that nothing was matched. Test: with an empty `docs/voice/examples/`, the
  report says no approved examples exist and the draft is unreviewed; no file in `examples/` is created.
  Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  (examples "one of the most reliable ways" to steer tone; 3 to 5) and https://arxiv.org/abs/2509.14543
  (styles approximated from samples in news and email) (verified 2026-11-03).
- [invariant] When the owner corrects your wording, offer to record the correction before you continue: show
  the `corrections.jsonl` line (date, surface, lang, before, after, reason, rule) and write it after the owner
  agrees. When the same rule recurs, or the owner says "always" or "never", promote it to a glossary row or a
  lint rule, as the `learning-loop` skill describes. Why: a correction that lives only in the chat is repeated
  next week. Test: the owner replaces "Slot" with "Termin" and says it is never "Slot"; the reply proposes the
  correction line and a glossary row, and `copy_lint.py --voice-check docs/voice` reports no VOI02 after it.
  Source: https://code.claude.com/docs/en/memory (instructions given only in conversation are lost) and
  https://www.skills.sh/erwannrousseau/skills/create-write-like-me (corrections as the strongest evidence)
  (verified 2026-11-03 in the research).

### Drafting and the native pass

- [default] Fix substance before surface. Collect the facts, write the one-line job of the text, draft plain,
  then lint. Treat a lint hit as a prompt to find the fact behind the sentence, not as a verdict on authorship.
  Do not swap a flagged word for a synonym. Trade-off: slower than a word swap. Deviate only with an ADR that
  names this trade-off. Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing ("descriptive, not
  prescriptive") (verified 2026-11-01).
- [default] Keep banned words out of the drafting step. Draft from the facts, the preferred glossary terms and
  the approved examples; run the word lists, the glossary's forbidden variants and the calque list afterwards
  through `copy_lint.py`. Do not try to fix tone with an instruction to "write naturally". Trade-off: some
  flagged words appear in the first draft and cost a revision. Deviate only with an ADR that names this
  trade-off. Source: https://arxiv.org/abs/2601.08070 (naming a forbidden word primed it in 87.5 % of
  violations; one 7B model) and https://arxiv.org/html/2503.04369 (a naturalness instruction left GPT-4 at 0.50
  against 0.53) (verified 2026-11-03).
- [default] After the draft, run a separate native pass: reread only the target-language text as a native
  editor and rewrite every sentence a native writer would not produce without a source text. German: nominal
  style, Funktionsverbgefüge, calques, genitive chains, English word order, wrong prepositions. English:
  corporate abstractions, nominalisation chains, stacked hedges, triplets, participle tails. Trade-off: one more
  pass per text. Deviate only with an ADR that names this trade-off. Source: https://arxiv.org/html/2503.04369
  (self-polishing cut translationese from 43 % to 25 %) and https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/
  (nominalisations 1.5 to 2 times, participial clauses 2 to 5 times the human rate) (verified 2026-11-03).
  Checklists: [references/de.md](references/de.md), [references/en.md](references/en.md).
- [default] Flag a word combination as a calque only with corpus evidence: rewrite at 1 : 10 or rarer against
  the natural form, judge by register between 1 : 3 and 1 : 10, leave it above that. Use the list in
  [references/collocations.md](references/collocations.md) and `scripts/collocation_check.py` for a new
  candidate; when the check is offline, say "no verdict". Trade-off: some odd phrasings stay because the
  corpus cannot decide them. Deviate only with an ADR that names this trade-off. Source: Google Books Ngram,
  de-2019 and en-2019, measured 2026-11-03 ("Entscheidung machen" 1 : 138, "einmal mehr" 1 : 2, so the first is
  rewritten and the second is ordinary German) and https://arxiv.org/html/2608.17399 (readers noticed "unusual
  words or word combinations") (verified 2026-11-03).
- [default] Test every sentence for substitution: put a competitor's name in place of the product's. If the
  sentence is still true, rewrite it with something only this product can say: a number with unit and
  baseline, a mechanism, a limit, a named integration. Trade-off: some sentences go and the page gets
  shorter. Deviate only with an ADR that names this trade-off. Source:
  https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ (verified 2026-11-01).
- [default] "More professional" means more precise, not more formal, longer or grander. When asked to make text
  sound more professional, keep the facts and the length, remove vagueness, fix register and typography, and
  add no superlative, buzzword, passive or nominal chain. Trade-off: the result may look plainer than the
  requester imagined, so say what you changed and why. Deviate only with an ADR that names this trade-off.
  Source: https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ (objective
  text scored 27 % higher, concise 58 %, both 124 %) and https://aka.ms/german-styleguide (conversational, not
  formal technical language) (verified 2026-11-01 and 2026-11-03).
- [default] Open with what the thing does and for whom; end on the last useful fact or the next action. No
  scene-setting opener, no rhetorical question, no summary closer. Sentences at or under 25 words. Contrast,
  triads and dashes are density signals, not bans: at most one "not X but Y" per page and none in a headline or
  first sentence. Trade-off: less warm-up. Deviate only with an ADR that names this trade-off. Source:
  https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice and
  https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style (verified 2026-11-01).

### Surfaces

- [default] Each surface has its register: UI labels, errors, empty states, toasts, mail, incident notices,
  docs, marketing and legal differ in length, nominal style and tone, as the table in
  [references/register.md](references/register.md) sets out. Errors, notices and docs carry no marketing word,
  no exclamation mark and no "please" padding. Trade-off: docs read plainer than the brand voice elsewhere.
  Deviate only with an ADR that names this trade-off. Source:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/ (models do not vary register by context) and
  https://developers.google.com/style/tone (verified 2026-11-03 and 2026-11-01).
- [default] UI strings: buttons are a verb with its object, errors say what happened and what to do, empty states
  say what appears and offer one action, confirmations name the object and what is lost, settings describe the
  on state, German leaves room for about 40 % more text. Trade-off: longer labels than "OK" or "Submit".
  Deviate only with an ADR that names this trade-off. Source:
  https://design-system.service.gov.uk/components/error-message/ and
  https://www.nngroup.com/articles/empty-state-interface-design/ (verified 2026-11-03). Details:
  [references/ui-microcopy.md](references/ui-microcopy.md).
- [default] Transactional mail has one purpose, carried by subject, first line and button alike; receipts carry
  no offers; German business mail carries the legally required company details. Trade-off: announcements need
  their own mail. Deviate only with an ADR that names this trade-off. Source:
  https://www.notifications.service.gov.uk/using-notify/guidance/edit-and-format-messages and
  https://www.gesetze-im-internet.de/uwg_2004/__7.html (verified 2026-11-03). Details:
  [references/transactional-mail.md](references/transactional-mail.md).
- [default] A changelog says what changed, for whom and how to use it, grouped (Added, Changed, Deprecated,
  Removed, Fixed, Security), newest first, ISO dates, customer-facing changes only. Trade-off: internal work
  stays invisible. Deviate only with an ADR that names this trade-off. Source:
  https://keepachangelog.com/en/1.1.0/ (verified 2026-11-01).

### Deutsche Texte

Diese Regeln sind auf Deutsch geschrieben, weil sie deutschen Text steuern. Dass das die Idiomatik verbessert,
ist eine ungeprüfte Annahme. Die Feldnamen (Why, Test, Trade-off, Source) bleiben englisch, weil der
Repository-Lint sie liest.

- [default] Anrede: du in Oberfläche, Mails, Website und Support bei Software für Selbstbedienung, kleine
  Firmen und Entwickler. AGB, Datenschutzerklärung und AVV dürfen beim Sie oder in der dritten Person bleiben,
  auf eigenen Seiten. Innerhalb einer Fläche wird nie gemischt. „du“ und „dein“ klein; in Mails groß nur, wenn
  `voice.md` das so festlegt. Sie für Konzern-IT, Steuer, Zahlungsverkehr oder Verwaltung nur per ADR. Why: du
  ist bei Slack, Notion, Shopify, Lexware Office, sevDesk und Hetzner üblich, Sie bei Microsoft, Stripe, SAP,
  DATEV und ELSTER; der sichtbare Fehler ist die Mischung. Trade-off: Sie wirkt bei kleinen Teams steif, du
  bei Behörden und Steuerberatern zu nah. Deviate only with an ADR that names this trade-off. Source:
  Live-Auszählung von 30 Websites in der Recherche (2026-11-03) und
  https://www.duden.de/sprachwissen/rechtschreibregeln/gross-und-kleinschreibung (D 83: klein, in Briefen groß
  erlaubt) (verified 2026-11-03).
- [invariant] Deutsche Typografie: „…“ oder »…«, keine englische Titelschreibung, Dezimalkomma, „19 €“, kein
  Apostroph vor dem Genitiv-s, Zusammensetzungen verbunden. Why: das sind Rechtschreib- und Lokalisierungsnormen,
  ein Verstoß ist ein Fehler, egal wer schreibt. Test: „Die "Online Rechnung" zeigt Kunden's Zahlungen, €19“
  ergibt mit `copy_lint.py --lang de` TYP01, TYP02, TYP03 und TYP05. Source: https://aka.ms/german-styleguide
  und https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf (§ 53) (verified 2026-11-01).
- [default] Deutsch wird aus dem deutschen Sachverhalt geschrieben, nicht aus einem englischen Entwurf übersetzt:
  Verb statt Substantivkette, Aktiv, Hauptsatz zuerst, englische Begriffe nur als Standardwort der Zielgruppe
  und deutsch gebeugt. Trade-off: mehr Arbeit als eine wörtliche Übersetzung. Deviate only with an ADR that
  names this trade-off. Source: https://aka.ms/german-styleguide („re-write just like you are writing the
  contents yourselves“) (verified 2026-11-03). Details und Prüftabelle: [references/de.md](references/de.md).

## Procedure

1. Name the surface, the language, the reader and the one job of the text: "This text makes [reader] do
   [action] because [fact]." If you cannot fill it, ask.
2. Load the voice files (`docs/voice/` or the project's path): `voice.md`, preferred glossary terms, corrections
   for this surface and language, 3 to 5 approved examples. None there: note "unreviewed voice" for the report.
3. Collect facts: behaviour, limits, real numbers with source and date, real UI labels, the reader's own words.
   Anything outside the list is a claim that needs a source ([references/claims.md](references/claims.md)).
4. Draft plain in the target language, from the facts, in the surface's register
   ([references/register.md](references/register.md); UI: [references/ui-microcopy.md](references/ui-microcopy.md);
   mail: [references/transactional-mail.md](references/transactional-mail.md)). German: write from the German
   facts, not from an English draft.
5. Native pass: reread only the target-language text and rewrite every sentence a native writer would not
   produce without a source ([references/de.md](references/de.md) or [references/en.md](references/en.md)).
6. Lint: `python3 ${CLAUDE_SKILL_DIR}/scripts/copy_lint.py --lang de|en [--glossary docs/voice/glossary.md] FILE`.
   In clients without `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder. Fix every SUP01,
   RES01, DSH02, CAL01, GLO01 and German TYP finding; read the rest as prompts. For a new suspicious combination
   run `scripts/collocation_check.py`.
7. Claim pass and substitution test: each superlative, number, customer and quote gets its source or
   `{TODO: source}`; each sentence that fits a competitor gets a fact or goes.
8. Read aloud. Run the linter again; keep a remaining hit only with a one-line reason.
9. Report: what was removed or marked `{TODO: source}`, remaining findings and why, facts still needed, and
   whether approved examples existed.
10. When the owner corrects the result, offer the `corrections.jsonl` line; promote a recurring rule
    ([references/voice-files.md](references/voice-files.md)).

## Traps

- Replacing a flagged word with a synonym. The empty claim is the tell, not the word.
- Making a sentence concrete with an invented number, customer, quote or approved example.
- Putting the ban list into the drafting prompt. It primes the words it bans; it belongs in the linter.
- Asking for "natural German" and skipping the native pass. The instruction alone changes nothing measurable.
- Flagging a phrase because it looks English. "einmal mehr" and "Sinn machen" are in normal use; check the
  corpus before calling something a calque.
- Hearing "more professional" as "more formal": Sie, passive voice, "zur Verfügung stellen", "utilise".
- Brochure tone in an error message, chat tone in a contract, cheer in an empty state.
- Mixing du and Sie because a legal template or a support macro was pasted in.
- Saying "noted" after a correction and not recording it.
- Driving the linter to zero, or telling an author the text "is AI".

## Done when

- Every number, comparison, superlative, customer, quote and award has a source or `{TODO: source}`.
- The text describes only what ships today; no chat residue or placeholder remains.
- Voice files were read, or their absence is reported and the draft is marked "unreviewed voice".
- The native pass ran on the final language; `copy_lint.py` was run before and after, with the glossary when
  one exists; remaining hits carry a reason.
- The register matches the surface; German text uses one address form, German typography and no listed calque.
- Owner corrections from this session are offered for `corrections.jsonl`.

## References

- [references/voice-files.md](references/voice-files.md): read before drafting in a product repo, and after an
  owner correction; file formats, loop, promotion to lint, privacy.
- [references/de.md](references/de.md): read for German copy (in German): address form, native pass,
  typography, sentence structure, examples.
- [references/en.md](references/en.md): read for English copy: patterns, native pass, calibrated markers,
  rewrites, genre notes.
- [references/collocations.md](references/collocations.md): read when a word combination looks translated or a
  CAL01 hit needs judging; corpus ratios DE and EN.
- [references/register.md](references/register.md): read to set the register of any surface; marketing,
  website, docs and notice guidance.
- [references/ui-microcopy.md](references/ui-microcopy.md): read for buttons, errors, empty states,
  confirmations, settings, toasts.
- [references/transactional-mail.md](references/transactional-mail.md): read for receipts, confirmations,
  reminders, account mail.
- [references/claims.md](references/claims.md): read when a draft contains a number, comparison, superlative,
  customer, testimonial or award.
- [assets/voice/voice.md](assets/voice/voice.md), [assets/voice/glossary.md](assets/voice/glossary.md),
  [assets/voice/corrections.jsonl](assets/voice/corrections.jsonl),
  [assets/voice/examples/_format.md](assets/voice/examples/_format.md): templates for `docs/voice/`.
- `scripts/copy_lint.py`: run on every draft; `--glossary`, `--voice-check DIR`, `--self-test`.
- `scripts/collocation_check.py`: compares a phrase with its alternative in Google Books Ngram; `--self-test`
  runs offline.

## Sources

- https://arxiv.org/html/2503.04369: naturalness instruction without effect; self-polishing 43 % to 25 %
  (verified 2026-11-03).
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/: instruction-tuned models, nominalisations and participial
  clauses above human rates, register not adapted (verified 2026-11-03).
- https://arxiv.org/html/2608.17399: generated German classified as translated (60.2 %, 37.6 %); readers cite
  unusual word combinations (verified 2026-11-03).
- https://arxiv.org/abs/2601.08070: naming a banned word primes it (one model) (verified 2026-11-03).
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices:
  3 to 5 examples; say what to do instead of what not to do (verified 2026-11-03).
- https://arxiv.org/abs/2509.14543 and https://arxiv.org/abs/2404.15269: style from samples; preferences from
  edits (verified 2026-11-03).
- https://books.google.com/ngrams: corpus for the calque ratios, de-2019 and en-2019, measured 2026-11-03.
- https://design-system.service.gov.uk/components/error-message/,
  https://www.nngroup.com/articles/empty-state-interface-design/,
  https://developer.apple.com/design/human-interface-guidelines/writing: UI text (verified 2026-11-03).
- https://www.notifications.service.gov.uk/using-notify/guidance/edit-and-format-messages: mail (verified
  2026-11-03).
- https://www.duden.de/sprachwissen/rechtschreibregeln/gross-und-kleinschreibung: du lowercase, capital allowed
  in letters (verified 2026-11-03).
- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing: signs are descriptive, generic content is the
  core problem (verified 2026-11-01).
- https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/: objective and
  concise web text tested (verified 2026-11-01).
- https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice and https://aka.ms/german-styleguide:
  voice, front-loading, German localisation (verified 2026-11-01 and 2026-11-03).
- https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style and https://developers.google.com/style/tone:
  sentence length, tone (verified 2026-11-01).
- https://keepachangelog.com/en/1.1.0/: changelog structure (verified 2026-11-01).
- https://www.gesetze-im-internet.de/uwg_2004/__5.html, /__6.html, /__7.html, /anhang.html and
  https://www.ecfr.gov/current/title-16/part-465: claims and mail advertising law (verified 2026-11-01 and
  2026-11-03).
- https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf: German orthography 2024 (verified
  2026-11-01).
