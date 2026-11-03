# Transactional mail: receipts, confirmations, reminders, account mail

## Contents

- One mail, one purpose
- Subject line
- Preheader
- Body
- German format and greeting
- Footer: what the law asks for in Germany
- Transactional or advertising
- Examples (constructed)
- Sources

Transactional mail is triggered by something the reader did or something that happened to their account:
an invoice, a booking confirmation, a password reset, a failed payment, an invitation to a project. The reader
opens it to find one fact or do one thing.

## One mail, one purpose

- Each mail has one job, written down before drafting: "This mail tells [reader] that [event] and lets them
  [action]." A receipt is not the place for a feature announcement.
- The event is in the subject, the first line and the button. If those three disagree, the mail is about two
  things.
- Same address form, terms and tone as the product UI. A mail is a surface of the product, not of the
  marketing team.

## Subject line

- Name the event and the object, in sentence case: "Rechnung 2026-0142 von Muster GmbH", "Your booking on
  12 November is confirmed", "Einladung zum Projekt „Website-Relaunch“".
- Put the distinguishing detail early (number, date, project name); mail clients truncate long subjects.
- No "Wichtig:", no "!", no emoji, no "Update" on its own.
- GOV.UK Notify asks for a heading that tells "recipients what your email or letter is about". The subject
  does that job before the mail is opened.

## Preheader

The preview text after the subject in most inboxes. Design judgment, Source: none.

- Continue the subject with the next useful fact: the amount and due date, the time and place, the expiry of
  a link. Do not repeat the subject.
- Set it explicitly. Otherwise clients show the first text they find, often "View in browser" or an alt text.

## Body

- First line: the event in one sentence, with the facts the reader came for. "Du hast den Termin am
  12. November um 14:30 Uhr bei Praxis Lindner gebucht."
- Then the one action, as a button with verb and object ("Termin ansehen", "Rechnung herunterladen", "Set new
  password"), and the same link as plain text for clients that block buttons.
- Then what happens next or by when: "Der Link gilt 60 Minuten."
- Then what to do if the reader did not expect this mail (password reset, sign-in, payment): one sentence.
- No greeting padding ("Wir hoffen, es geht dir gut", "I hope this email finds you well"), no "Vielen Dank,
  dass Sie sich für ... entschieden haben" before the fact.
- No bold, italics or underline for emphasis; numbered steps when there are steps (GOV.UK Notify).
- Plain words; the register table in the register reference applies.

## German format and greeting

- Dates "03.11.2026" or "2026-11-03", or written out ("3. November 2026"); times "14:30 Uhr", "8 Uhr"
  (DIN 5008, summary by Universität Passau). Pick one style in `voice.md` and keep it.
- Money "1.234,50 €". For counts DIN 5008 prefers a space ("1 500"), Microsoft a point ("1.500"): a house
  choice, stated once in `voice.md`.
- Greeting: "Hallo Anna," fits du; "Guten Tag Frau Lindner," fits Sie. The text after the comma starts
  lowercase.
- Sign-off without a comma: "Viele Grüße" then a new line with the name or team. (Duden's comma rule here was
  read via secondary sources, not verified directly.)
- In letters and mail, du and dein may be capitalised (Duden D 83, Rechtschreibrat § 66). Decide once in
  `voice.md`; the product UI stays lowercase either way.

## Footer: what the law asks for in Germany

Review-ready draft, not legal advice. Scope: Germany, business senders.

- Mail from a company to a named recipient counts as a business letter "gleichviel welcher Form" (in whatever
  form). A GmbH states legal form, registered office, register court, register number and all managing
  directors (§ 35a GmbHG); a registered merchant states the firm name, the "eingetragener Kaufmann"
  designation, the place of business, register court and number (§ 37a HGB). Other legal forms have parallel
  rules; check the one that applies.
- Keep the footer short and the same in every mail. It is a legal block, not a place for slogans.
- A link to the privacy notice belongs in the footer of mail that processes personal data, which is all of it.

## Transactional or advertising

- A mail that promotes products is advertising, even when it rides on a receipt. In Germany, advertising by
  mail needs consent, except for existing customers when all four conditions of § 7 (3) UWG hold: the address
  came from a sale, the mail promotes the sender's own similar products, the customer has not objected, and
  the customer is told clearly, when the address is collected and in every mail, that they can object at any
  time without costs other than basic transmission costs.
- So: keep receipts and confirmations free of offers. If a mail must carry one, the objection notice from
  § 7 (3) Nr. 4 UWG goes into that mail.

## Examples (constructed)

Invoicing app, invoice sent to a customer (DE, Sie, because the voice file says so for invoice recipients)

- Subject: "Rechnung 2026-0142 von Muster GmbH über 1.190,00 €"
- Preheader: "Fällig am 17.11.2026. Die Rechnung liegt als PDF bei."
- First lines: "Guten Tag Frau Lindner," then "hier ist unsere Rechnung 2026-0142 über 1.190,00 €. Bitte
  überweisen Sie den Betrag bis zum 17.11.2026." ("anbei erhalten Sie" is office filler; "bitte" is right here,
  because the reader is asked to do something)
- Button: "Rechnung ansehen"

Booking system, confirmation (EN)

- Draft subject: "Thank you for your booking!"
- Rewrite subject: "Booking confirmed: Tue 12 Nov, 14:30, Lindner Physiotherapy"
- First line: "You're booked for Tuesday, 12 November at 14:30 with Anna Lindner."
- Button: "Add to calendar". Next line: "Need to change it? Move or cancel up to 24 hours before."

Project tool, invitation (DE, du)

- Draft: "Hey! Du wurdest eingeladen. Wir freuen uns riesig, dich an Bord zu haben!!"
- Rewrite subject: "Jonas lädt dich zum Projekt „Website-Relaunch“ ein"
- First line: "Jonas hat dich zum Projekt „Website-Relaunch“ eingeladen. Dort warten 12 offene Aufgaben."
- Button: "Einladung annehmen". Next line: "Die Einladung gilt 7 Tage."

## Sources

- https://www.notifications.service.gov.uk/using-notify/guidance/edit-and-format-messages: heading says what the
  mail is about; no bold, italics or underline; numbered steps (verified 2026-11-03 in the research).
- https://www.uni-passau.de/fileadmin/dokumente/beschaeftigte/kommunikation_marketing/webredaktion/DIN_5008.pdf:
  DIN 5008 dates, times, number grouping (verified 2026-11-03 in the research).
- https://www.gesetze-im-internet.de/gmbhg/__35a.html: business letters "gleichviel welcher Form" (verified
  2026-11-03).
- https://www.gesetze-im-internet.de/hgb/__37a.html: same for registered merchants (verified 2026-11-03).
- https://www.gesetze-im-internet.de/uwg_2004/__7.html: § 7 (3) UWG, four conditions for existing-customer
  advertising (verified 2026-11-03).
- https://www.duden.de/sprachwissen/rechtschreibregeln/gross-und-kleinschreibung: D 83, du and dein lowercase,
  capitalisation allowed in letters (verified 2026-11-03).
