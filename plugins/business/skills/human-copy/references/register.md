# Register per surface, and notes for marketing, website and docs

## Contents

- Why register drifts
- Register table
- German address form by surface
- Marketing pages and website
- Docs
- Incident and status notices
- Sources

## Why register drifts

Instruction-tuned models keep one dense, noun-heavy register wherever they write. Reinhart et al. measured
nominalisations at 1.5 to 2 times and present participial clauses at 2 to 5 times the human rate, and found
that the models "do not vary their linguistic output in response to contextual factors in ways similar to
humans" (PNAS 2025). The result is an error message that reads like a brochure and a landing page that reads
like a contract. The table below fixes the register per surface before drafting starts.

## Register table

Examples are constructed for this skill (invoicing app, booking system, project tool). A product's approved
examples in `docs/voice/examples/` take precedence.

| Surface | Length | Nominal style | Tone | German example | English example |
|---|---|---|---|---|---|
| UI labels, buttons | 1 to 4 words | none; infinitive plus object | neutral | „Termin verschieben“ | "Move booking" |
| Error messages | 1 to 2 sentences, under 20 words each | none | calm, specific, no "sorry", "oops" or "!" | „Rechnung nicht gesendet. Prüf die E-Mail-Adresse des Kunden.“ | "Invoice not sent. Check the customer's email address." |
| Empty states | 1 sentence plus one button | none | helpful, no cheer | „Hier erscheinen deine Aufgaben. Leg die erste an.“ | "Your tasks appear here. Add the first one." |
| Toasts | 2 to 4 words | none | past tense, factual | „Aufgabe verschoben“ | "Task moved" |
| Transactional mail | short paragraphs, first line carries the event | low | friendly, plain, like a colleague's note | „Du hast den Termin am 12. November um 14:30 Uhr gebucht.“ | "You're booked for 12 November at 14:30." |
| Incident or status notice | short sentences, time with zone | none | factual, no reassurance without facts | „Seit 9:40 Uhr MEZ kommen Rechnungsmails verspätet an. Nächstes Update um 10:30 Uhr.“ | "Since 09:40 CET, invoice emails arrive late. Next update at 10:30." |
| Docs | steps of one action each; sentences up to 25 words | low; fixed technical terms allowed | instructive, neutral, no marketing words | „Öffne **Einstellungen** und wähle **Zahlungsarten**.“ | "Open **Settings** and select **Payment methods**." |
| Marketing, website | sentences up to 25 words; one figure per claim | low | confident through facts, at most one "!" per page | „Rechnungen mit deinem Logo, als PDF per Mail. Ab 9 € im Monat.“ | "Invoices with your logo, sent as PDF. From €9 a month." |
| Changelog | one line per change | low | factual, present or perfect | „Termine lassen sich jetzt per Drag-and-drop verschieben.“ | "You can now drag a booking to another slot." |
| Legal (AGB, Datenschutz, AVV) | as precise as needed | allowed where the term is exact | formal, defined terms | „Der Kunde kann den Vertrag mit einer Frist von einem Monat kündigen.“ | "The customer may terminate the agreement with one month's notice." |

Reading the columns:
- Length is a ceiling, not a target.
- "Nominal style: none" means a verb carries the action: „Gespeichert“, not „Speicherung erfolgreich“.
- Tone describes the reader's situation: someone who just hit an error wants the fix, not empathy phrases.

## German address form by surface

[default] du across product UI, mail, website and support for self-serve, small-business and developer
software; legal texts may use Sie or neutral third person ("der Kunde") on their own pages; no surface mixes
forms. Sie for enterprise, tax, payments or public-sector audiences only through an ADR. Details and evidence:
the German reference.

| Surface | du product | Sie product |
|---|---|---|
| UI, errors, empty states | du | Sie |
| Mail | du (Du/Dein capitalised allowed in letters, as house choice) | Sie |
| Website, marketing | du | Sie |
| Docs, help centre | du | Sie |
| Support replies | du, unless the customer writes Sie and the house rule allows mirroring | Sie |
| Legal pages | Sie or third person, isolated | Sie or third person |

## Marketing pages and website

- First sentence: what the product does and for whom. One figure with unit and baseline above the fold, from
  the facts list. The claims reference covers sourcing.
- Headings say what the section shows, in sentence case. A heading that would fit a competitor's page is
  rewritten.
- Show real interface, real numbers and real limits next to claims. Every feature block: what it does, a
  concrete example, where to find it, which plan has it.
- Buttons name the action and object ("Rechnung schreiben", "Start a project"), not "Get started" alone.
- German pages are written from the German facts. The Microsoft German style guide asks for German that reads
  as if written from scratch, not translated, and allows dropping what does not carry.
- A deliberate deviation from the house style as an eye-catcher is allowed on marketing pages when it fits the
  brand (German UPA heuristic 6); product flows stay functional.

## Docs

- Imperative steps, one action per step, interface labels in bold exactly as shown.
- No "simply", "just", "einfach", "schnell": they tell the reader the step is easy, and readers for whom it
  is not feel blamed.
- Explain an abbreviation on first use. Keep the product's terms from the glossary; do not introduce synonyms
  for variety.
- Same address form as the UI. GitHub's German docs show the failure: "Beginnen Sie Ihre Reise" next to
  "Festlegen deines Benutzernamens" on the same page (measured 2026-11-03 in the research).

## Incident and status notices

- What is affected, since when (time and zone), what the reader can do now, when the next update comes.
- No reassurance without a fact ("Wir arbeiten mit Hochdruck daran" is not information). Say what is being
  done if it is known.
- Updates are dated and keep their earlier text; corrections are marked as corrections.

## Sources

- https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/: Reinhart et al., PNAS 122(8), 2025, nominalisation and
  participle rates, register not adapted (verified 2026-11-03 in the research).
- https://aka.ms/german-styleguide: rewrite rather than translate (verified 2026-11-03 in the research).
- https://germanupa.de/sites/default/files/2024-05/leitfaden_ux-writing_heuristiken_v1.01_0.pdf: heuristic 6,
  consistent terminology and address form; deliberate deviation as eye-catcher (verified 2026-11-03 in the
  research).
- https://developers.google.com/style/tone: no exclamation marks in docs, "please" sparingly (verified
  2026-11-01).
- https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style: 25-word sentences (verified 2026-11-01).
