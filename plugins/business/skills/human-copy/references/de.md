# German copy: typography, phrasing, grammar, address, genres

## Contents

- Calibration
- Where the word lists live
- Typography and punctuation
- Phrasing: calques and templates
- Grammar and sentence structure
- Address form and terms
- Rewrite examples (constructed)
- Genre notes: landing page, feature page, changelog, mail, docs
- Review checklist

Rules are written in English; German examples are in German. Native-sounding B2B German comes from German
sentence structure, not from replacing English words one by one.

## Calibration

- No single marker proves that a text is machine-made. The German Wikipedia guide states that not every text with
  the listed indicators is AI-generated, and that detectors are not sufficient proof
  (https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte, verified 2026-11-01).
- German word lists are thin evidence. Most lists of "AI words" in German are translations of English findings
  or editorial impressions. The strong German rules are typography and grammar, which rest on orthography and
  style norms and hold for any author. Vocabulary rules below are prompts.
- Beware lists of AI phrases that were themselves generated. Do not import a phrase list without a source that
  shows how it was built.
- Domain words are not tells. "Zuverlässig" is a core word for a monitoring product. Check the claim around it:
  "Zuverlässig" with no number is a hope; "99,9 % der Prüfungen liefen im März unter 5 Sekunden" is a claim.
- The goal is good German B2B copy: specific, active, in one voice. Human-written German SaaS pages show the same
  faults (mixed du and Sie, English headings next to German ones, split compounds).

## Where the word lists live

Buzzwords, stock openers, significance phrases, hedges, vague authorities and calques are in
`scripts/copy_lint.py` (German section), with a last-reviewed date in the header: 2026-11-01. Run
`python3 scripts/copy_lint.py --lang de FILE`. Sourced German examples of commercial phrases that the
editorial press names as typical for machine text include "auf das nächste Level", "integraler Bestandteil",
"vielfältige Möglichkeiten" and "In der heutigen Zeit"
(https://t3n.de/news/ki-texte-erkennen-floskeln-buzzwords-gedankenstriche-chatgpt-1745388/, verified 2026-11-01),
and "perfekt geeignet" and "optimal abgestimmt"
(https://www.gamestar.de/artikel/ki-texte-und-buecher-ekennen,3457410.html, verified 2026-11-01). These are
editorial observations, not measurements. Phrases presumed to be calques of English tells, such as "Tauche ein"
or "nahtlos", are Unverified as German machine-text markers; the linter flags them as empty marketing words,
which they are in any case.

## Typography and punctuation

These rules are mechanical and norm-based. Findings carry the TYP, DSH and TTL codes.

- Dashes. The German thought dash is the en dash with a space on each side. The Microsoft German style guide
  states that the em dash is not used in German documentation and that the en dash marks an isolated element
  (https://aka.ms/german-styleguide,
  verified 2026-11-01). German Wikipedia calls the long em dash unusual in German running text
  (https://de.wikipedia.org/wiki/Halbgeviertstrich, verified 2026-11-01). Ranges use the en dash without spaces
  ("37–39"). The linter flags any em dash in German text (DSH01).
- Dash plus comma. House rule, not orthography: no "–," or "—,", and no paired dash insertion in customer copy.
  The official rulebook allows the construction ("Er weigert sich – leider –, nach Frankfurt zu kommen"), so
  reviewers must not call it a spelling error. It is avoided because the sentence reads as broken. Write the
  aside as its own sentence. Flags: DSH02, DSH03.
- Quotes. „…“ (low-high) or »…« used consistently; never English “…”. The Microsoft guide names „Anführungszeichen“
  as the favoured form and straight quotes as the alternate solution. For UI labels, writing the label verbatim in
  bold avoids the question. Flag: TYP01.
- Headings. Capitalise the first word and nouns, as in running text; do not copy English title case. Source:
  Rechtschreibrat § 53 (first word of a heading is capitalised) and Microsoft 4.2.4 ("Do not apply the same
  principle to German titles ... The same rule applies to software strings") (verified 2026-11-01). Flag: TTL01.
  The check only catches capitalised function words; capitalised adjectives need a reader.
- Genitive and plural -s. Genitive without apostrophe ("Annas Statusseite"); no apostrophe in plurals ("die APIs").
  The apostrophe is correct in a few cases (after s, ß, x, z; before genitive -s on a name written as a whole,
  Rechtschreibrat § 80), so the linter marks it for a look (TYP02).
- Compounds. One word or hyphenated, never split by a space: "KI-Agenten", "Statusseite", "Incident-Management".
  Microsoft: compounds of up to three parts in one word. Flag: TYP03; extend the prefix list in the script from
  the product glossary.
- Label punctuation. No comma or period directly after a label ending in ? ! … ("Unter Wie lange? legst du fest ...").
  Flag: TYP04.
- Numbers and currency. Decimal comma, thousands point, currency after the amount with a space: "199,95 €",
  "9.999,99 €" (Microsoft German guide, de-DE; Swiss usage differs). Write "19 € im Monat", not "€19/Monat".
  Flag: TYP05. Whether to avoid dotted dates or "Mio." in ad copy is a house choice, not a rule here.

## Phrasing: calques and templates

- Calques. Replace English grammar in German words with the German idiom: "einmal mehr" for "once more" becomes
  "wieder" or "erneut" (https://de.wikipedia.org/wiki/Denglisch, verified 2026-11-01). Flag: CAL01. The
  wider calque list is Unverified beyond what the cited Microsoft and Wikipedia pages show; check any further
  candidate in a dictionary before you flag it in review.
- Chat residue. "Natürlich! Hier ist eine überarbeitete Version:" and "Ich hoffe, das hilft" are deleted outright
  (RES01).
- Contrast frames. "nicht nur ..., sondern auch", "Es ist nicht X, es ist Y", "mehr als ein X, es ist ein Y":
  state the claim directly; keep a contrast only if readers hold the rejected view (NXY01). The editorial press
  names "Nicht nur, sondern auch" and "Wenn, dann" as frequent in machine text (t3n page above); human German
  uses both, so density counts, not presence.
- Rule of three. "Einfach. Schnell. Sicher." and "schnell, sicher und zuverlässig" are replaced by one claim with a
  fact: "Prüfintervall ab 30 Sekunden." (TRI01).
- Significance and summary. "spielt eine entscheidende Rolle", "unterstreicht", "Zusammenfassend lässt sich sagen":
  say what the feature does. No "Fazit" section in product copy.
- Hedge stacks. "könnte in vielen Fällen dazu beitragen, ... potenziell zu reduzieren": use the indicative and
  state the condition. The Microsoft guide calls the subjunctive not appropriate for its style and prefers
  active voice with imperative or indicative.
- Ranges and sweeps. "Egal ob Startup oder Konzern" is replaced by the real range: "Für Teams von einer bis
  fünfzig Personen." (only if true).
- Connectors. "Darüber hinaus", "Zudem", "Außerdem" at the start of consecutive sentences: allow about one per 150
  words (CON01; the threshold is Source: none; design judgment).
- Superlatives. "die beste Monitoring-Lösung am Markt" is flagged until it carries a basis (SUP01). The Bavarian
  plain-language guide advises against fashion words and superlatives and asks whether the highest degree of
  comparison "übertrieben und damit unglaubwürdig wirkt" (https://mik.brandenburg.de/sixcms/media.php/9/BuergernaheSpracheinderVerwaltung.pdf,
  verified 2026-11-01). Double superlatives ("optimalste", "einzigste") are wrong in any register.

## Grammar and sentence structure

- Verbs instead of noun chains. "Mitteilung machen" becomes "mitteilen"; "in Kenntnis setzen" becomes
  "informieren"; "einer Prüfung unterziehen" becomes "prüfen" (Bavarian guide, section 3.4). Do not string more
  than four nouns together; split into a second sentence. Flag: FVG01 (a short list of stock constructions).
- Active with a named actor. "Seitens des Systems wird eine Benachrichtigung versendet" becomes "Das System
  schickt dir eine Nachricht." Use "wir" for the company and "du" or "Sie" for the reader; avoid "man" in
  instructions (Bavarian guide, 3.3).
- Sentence length. At most 25 words, aim for about 15; main clause first, no subordinate clause wedged in the
  middle. The 25-word limit is stated for English by GOV.UK; for German the Bavarian guide has a section on
  sentence length (3.5) and on main clause before subordinate clause (3.6). LEN01 flags more than 15 % of
  sentences over 25 words.
- One sentence, one thought. Comma splices become two sentences. Repeat the noun when a pronoun could point at
  two things.
- Tense. Product copy in the present; changelogs in the present or perfect, consistently.
- Negation. Say what is: "Das ist umsonst" instead of "Das kostet nichts" only if both are true; avoid double
  negatives.

## Address form and terms

- One address form per product. Decide du or Sie and apply it to UI, mail, docs, errors and the cookie banner.
  Statutory templates may stay formal; keep them isolated. "Sie" and "Ihr" are always capitalised; "du" and
  "dein" are lowercase, except that in letters they may be capitalised (Rechtschreibrat §§ 65 and 66, verified
  2026-11-01). A capitalised "Du" in web copy is therefore wrong (ADR02). Mixed forms are flagged by ADR01; a
  sentence-initial "Sie" is ambiguous (she, they) and is not counted.
- Buttons and short labels: verb plus object, no pronoun ("Link kopieren", not "Kopiere deinen Link").
- One term per concept; keep a glossary. Brand and product names exactly as the brand writes them; check the
  source before the first draft.
- Anglicisms. Keep an English term only if it is the target group's standard word or the product's UI label,
  inflect it by German grammar, and give German pages German headings. The Microsoft guide: acceptable "if they
  are indeed the industry standard in Germany", and no substitute for researching that standard.
- Jargon. In general copy use the plain word; keep the legal or technical term where it is exact (contracts, the
  data processing agreement name in legal text). A term used to impress and not exact opens a flank.
- Gender signs: choose one house style and keep it. The official rulebook does not include word-internal signs in
  the core of German orthography; mixing "Kund:innen" with "Kunden" in one text is the visible fault. Source: none
  for the mix as a machine tell; design judgment.

## Rewrite examples (constructed)

All pairs are constructed for this skill. Values in curly braces stand for real, sourced values.

Hero text

- Draft: "In der heutigen schnelllebigen Welt ist zuverlässiges Monitoring nicht nur ein Nice-to-have, es ist ein
  echter Mehrwert. Tauche ein in eine Welt, in der Ausfälle der Vergangenheit angehören."
- Rewrite: "Wir prüfen deine Website von {vier} Standorten aus, auf Wunsch alle {30} Sekunden. Fällt sie aus,
  bekommst du eine SMS oder einen Anruf."
- Changed: opener, contrast, buzzword and calque are gone; interval and channel are stated; du throughout.

Nominal style

- Draft: "Die Durchführung der Überprüfung der Erreichbarkeit erfolgt seitens des Systems in regelmäßigen
  Abständen."
- Rewrite: "Das System prüft regelmäßig, ob dein Dienst erreichbar ist."
- Changed: verb carries the action; the actor is named; one sentence, one thought.

Typography

- Draft: "Die "Status Seite" zeigt Kunden's Störungen. Das kostet €19 pro Monat. Wir haben in 2026 einmal mehr 1,000
  Checks pro Minute ausgeführt."
- Rewrite: "Die Statusseite zeigt Störungen deiner Kunden. Das kostet 19 € im Monat. Wir haben 2026 wieder 1.000
  Prüfungen pro Minute ausgeführt."
- Changed: compound joined, no apostrophe, German price and number format, calques replaced. (The count itself
  needs a source in real copy.)

Unsourced superlative

- Draft: "Die beste Monitoring-Lösung am Markt."
- Rewrite A: "Laut unserem Test vom {Monat Jahr} meldet die Seite einen Ausfall im Median nach {N} Sekunden
  ({Link zur Methode})."
- Rewrite B: "Prüfung von {vier} Standorten in Europa und den USA."
- Changed: a claim with a checkable basis, or the product's own measured behaviour.

Dash insertion

- Draft: "Wer das Produkt aus eigener PHP-Software heraus steuert – etwa um für Kunden Services anzulegen –, soll
  dafür kein rohes JSON zusammenbauen müssen."
- Rewrite: "Services für deine Kunden legst du jetzt direkt aus PHP an. Rohes JSON brauchst du dafür nicht mehr."
- Changed: aside becomes its own sentence; active, du, two clear statements.

Conditional frame

- Draft: "Wenn es zu deinem Konto gehört, eröffne ein Ticket im Support-Bereich."
- Rewrite: "Ein Anliegen zu deinem Konto eröffnest du als Ticket im Support-Bereich."
- Changed: no conditional where the reader can simply act.

## Genre notes

Landing page

- First sentence: what it does and for whom, in one main clause. One figure with unit and baseline above the
  fold, from the facts file. Headings in German sentence case, not English title case and not two-part "X: Y".
- Buttons: verb plus object ("Statusseite anlegen"). Standing alone, "Mehr erfahren" and "Jetzt starten" say
  nothing about the target; the WCAG link-purpose criterion asks that the purpose be determinable from the link
  text or its context (https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html, verified
  2026-11-01). Flag: CTA01.
- Numbers as digits with German separators; price on its own line or as "19 € im Monat", with "alle Preise
  netto" stated once when the audience is business.

Feature page

- Each feature: what it does, a concrete example or number, where to find it. Name the real range of the
  workflow instead of "Egal ob ...". Show the real interface labels, set in bold exactly as they appear.

Changelog and release notes

- Present or perfect tense, consistently. Per entry: object, what changed, what the reader can do. Only changes
  customers can see or use; nothing about internal tools or infrastructure. No benefit that has not shipped.
  Group and date as in the English reference (Keep a Changelog structure works in German with translated
  headings: Hinzugefügt, Geändert, Veraltet, Entfernt, Behoben, Sicherheit).
- Heading, intro and item titles do not repeat each other.

Mail

- Subject says what is inside, in German sentence case. First line answers or announces. One address form, the
  same as in the product. Register matches the channel: avoid slang in a company mail, and check a colloquial
  word before you use it.
- Cold outreach: the recipient's company name exactly as the company writes it.

Docs

- Du or Sie as in the UI. Imperative for steps, one action per step, verbs first. Bold only for interface labels.
  No marketing words, no exclamation marks, no "bitte" padding. Explain abbreviations on first use. Errors state
  what happened and what to do next.

## Review checklist

- Each number, customer, quote, superlative and comparison has a source or `{TODO: source}`.
- No chat residue, placeholder or "Fazit" section.
- Typography: „…“ quotes, en dash with spaces, no em dash, no dash plus comma, no apostrophe -s, compounds joined,
  "19 €", decimal comma and thousands point.
- Headings in German sentence case, no emoji, no two-part "X: Y" pattern without need.
- One address form, du lowercase, Sie capitalised, buttons without pronoun where natural.
- Verbs over noun chains, active with a named actor, sentences at or under 25 words, main clause first.
- One term per concept; brand names as the brand writes them; one gender style.
- Nothing unbuilt, nothing internal.
- Read aloud; check flow at labels and pronouns.
