# UI microcopy: buttons, errors, empty states, confirmations, settings, toasts

## Contents

- What holds for every string
- Buttons and links
- Error messages
- Empty states
- Confirmations before destructive actions
- Settings labels and descriptions
- Toasts and inline success
- Length and German text expansion
- German UI specifics
- Examples (constructed, three products)
- Sources

Examples use an invoicing app, a booking system and a project tool. They are constructed for this skill, not
approved shipped text; a product's own approved texts in `docs/voice/examples/` outrank them.

## What holds for every string

- One term per concept across the whole product. Shopify: "Use a single noun, verb, or phrase to describe a
  specific thing, action, or concept"; its counterexample is "Upload images" next to "Add photos". Apple: keep a
  list of common terms and use it. The glossary in the voice files is that list.
- Say what the reader can do, in the reader's words, not the system's ("Rechnung", not "Beleg-Objekt").
- No "we" in errors. Apple's example: "Unable to load content" over "We're having trouble loading this
  content". "We" fits mail and marketing, where a company speaks.
- No jokes or "oops" where something went wrong. Apple calls "oops!" insincere; GOV.UK lists "oops" among the
  words to avoid in errors.
- Strings are full sentences or clear labels, never fragments joined at runtime. Microsoft's
  internationalization checklist: "Don't concatenate strings to form sentences", because word order differs by
  language.

## Buttons and links

- A verb, usually with its object: "Rechnung senden", "Send invoice", "Termin verschieben", "Move booking".
  Apple: a verb is "almost always best" ("Send" over "Let's do it!"). Shopify: CTAs "start with a strong verb".
- The label names the result, so the reader knows what happens before clicking. "Weiter" and "Continue" are
  fine inside a wizard where the next step is visible; "Mehr erfahren" and "Learn more" alone on a page are not
  (CTA01).
- Possessives sparingly: "Favoriten", not "Deine Favoriten"; "Settings", not "Your settings" (Apple).
- The primary and secondary buttons of a dialog use parallel verbs: "Projekt löschen" / "Abbrechen", not
  "Ja" / "Nein".

## Error messages

Two parts: what happened, and what the reader can do now. GOV.UK: "Describe what has happened and tell them
how to fix it." Apple: say how to fix it ("Choose a password with at least 8 characters").

- Name the object and the failure: "Die Rechnung wurde nicht gesendet." beats "Ein Fehler ist aufgetreten."
- Give the next step the reader can take, with the real control name: "Prüf die E-Mail-Adresse des Kunden
  und sende die Rechnung erneut."
- If the reader can do nothing, say what happens next and when: "Wir versuchen es in 5 Minuten noch einmal."
- No blame ("you forgot", "du hast vergessen"), no "invalid" or "ungültig" without saying what is valid, no
  "please" and no "sorry": GOV.UK names all of these, because they add words without helping.
- No codes in the sentence. Put a reference ID after it if support needs one: "Fehler-ID: 7F3K".
- Validation messages sit next to the field and say what the field needs: "Gib ein Datum ab heute ein."
- Register: calm and plain. No exclamation marks, no capitals for emphasis.

## Empty states

NN/g's three guidelines (Kaplan 2021): explain why the space is empty, explain how to fill it, and give a
direct action.

- First line: what will appear here. "Hier erscheinen deine Rechnungen, sobald du die erste schreibst."
- One action that fills it: "Rechnung schreiben". One, not three. A second, quieter link to help is fine.
- Distinguish "nothing yet" from "nothing matches the filter" from "still loading". A filter empty state
  offers to reset the filter; a loading state never says "keine Einträge".
- No illustration caption in place of the explanation, no "Noch ganz schön leer hier!".

## Confirmations before destructive actions

- The title asks about the specific object: "Projekt „Website-Relaunch“ löschen?"
- The body says what is lost and whether it can be undone: "Die 48 Aufgaben und alle Kommentare werden
  gelöscht. Das lässt sich nicht rückgängig machen."
- The confirm button repeats the verb and object: "Projekt löschen". Never "OK" or "Ja".
- Confirm only what cannot be undone. For actions that can be undone, act and offer "Rückgängig" in a toast.

## Settings labels and descriptions

- The label describes the on state: "Erinnerungen per SMS senden", not "SMS-Erinnerungen deaktivieren"
  (Apple: settings labels describe the on state).
- A description line says what changes for whom, with numbers: "Gäste bekommen 24 Stunden vor dem Termin eine
  SMS."
- No double negatives ("Keine Benachrichtigungen nicht anzeigen").

## Toasts and inline success

- Past tense, object first, short: "Rechnung gesendet", "Booking moved", "Aufgabe verschoben".
- Add an action only if it is useful now: "Rückgängig", "Anzeigen".
- No "Erfolgreich!" on its own, no "Super!", no exclamation mark.
- A toast disappears; anything the reader must act on goes into the page, not the toast.

## Length and German text expansion

- Plan for German strings to be longer. Microsoft's internationalization checklist: "English strings often
  expand by 40% when translated into German or Dutch." Its internationalization testing page adds that German
  text "is likely to be longer and uses a different sentence structure".
- When German does not fit, rewrite it shorter in German ("Teilen" for "Share with team" when the context
  shows the team). Do not abbreviate ("Einst.") and do not switch to English to save space.
- Write the German string from the situation, not from the English string. The Microsoft German style guide
  asks translators to "re-write just like you are writing the contents yourselves".
- Never shrink by dropping the object from a button when two buttons would then read the same.

## German UI specifics

- Buttons and menu items: infinitive plus object, no pronoun: "Link kopieren", "Termin absagen". Not "Kopiere
  den Link" and not "Kopieren Sie den Link".
- Sentences addressed to the reader use the product's one address form (see the German reference and
  `voice.md`). du is lowercase.
- Nouns in compounds: "E-Mail-Adresse", "Rechnungsnummer", never "Rechnungs Nummer".
- Typography: „…“ for quoted names, "19 €", "14:30 Uhr", dates as the house style says.
- Anglicisms only when they are the reader's word and the product shows them that way ("Dashboard" may be
  fine, "Slot" for a booking time usually is not). Inflect them in German.
- Avoid nominal style in UI: "Speicherung erfolgreich durchgeführt" becomes "Gespeichert".

## Examples (constructed, three products)

Invoicing app, error after sending fails

- Draft (EN): "Oops! Something went wrong. Please try again later."
- Rewrite (EN): "Invoice not sent. The customer's email address bounced. Check the address and send it again."
- Draft (DE): "Ups! Beim Versenden der Rechnung ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut."
- Rewrite (DE): "Rechnung nicht gesendet. Die E-Mail-Adresse des Kunden ist nicht erreichbar. Prüf die Adresse
  und sende die Rechnung erneut."
- Changed: object and cause named; one next step with the real action; no "Ups", no "bitte"; one address form.

Booking system, empty calendar

- Draft (DE): "Hier ist es noch ganz schön leer! Starte jetzt durch und erstelle deinen ersten Slot."
- Rewrite (DE): "Hier erscheinen deine Termine, sobald Gäste buchen. Leg zuerst fest, wann du buchbar bist."
  Button: "Zeiten festlegen"
- Changed: says what appears and what fills it; the anglicism "Slot" and the cheer are gone; one action.

Project tool, delete confirmation

- Draft (EN): "Are you sure? This action cannot be undone." Buttons: "OK" / "Cancel"
- Rewrite (EN): "Delete project “Website relaunch”? Its 48 tasks and all comments will be deleted. You can't
  undo this." Buttons: "Delete project" / "Cancel"
- Changed: object named, loss counted, button repeats verb and object.

## Sources

- https://developer.apple.com/design/human-interface-guidelines/writing: verbs on buttons, no "we" in errors,
  "oops" insincere, possessives sparingly, settings describe the on state, list of common terms (verified
  2026-11-03 in the research).
- https://shopify.dev/docs/apps/design/content: one term per concept, strong verbs, avoid idioms (verified
  2026-11-03 in the research).
- https://design-system.service.gov.uk/components/error-message/: "Describe what has happened and tell them how
  to fix it"; avoid "please", "sorry", "valid"/"invalid", "oops", blame words (verified 2026-11-03).
- https://www.nngroup.com/articles/empty-state-interface-design/: explain why empty, how to fill, direct action
  (Kaplan, 2021-09-19; verified 2026-11-03).
- https://learn.microsoft.com/en-us/windows/win32/intl/internationalization-checklist: 40 % expansion into
  German; do not concatenate strings (verified 2026-11-03).
- https://learn.microsoft.com/en-us/globalization/testing/how-to-perform-internationalization-testing: German
  text longer, different sentence structure; no concatenation (verified 2026-11-03).
- https://aka.ms/german-styleguide: rewrite instead of translating; anglicisms only when industry standard
  (verified 2026-11-03 in the research).
- https://germanupa.de/sites/default/files/2024-05/leitfaden_ux-writing_heuristiken_v1.01_0.pdf: consistent
  terminology and address form across channels (verified 2026-11-03 in the research).
