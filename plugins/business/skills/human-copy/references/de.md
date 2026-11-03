# Deutsche Texte: Anrede, muttersprachlicher Durchgang, Typografie, Satzbau

## Contents

- Warum diese Datei auf Deutsch ist
- Einordnung
- Anrede: du, Sie und Rechtstexte
- Der muttersprachliche Durchgang
- Typografie und Zeichensetzung
- Satzbau und Grammatik
- Begriffe, Anglizismen, Gendern
- Umschreibbeispiele (konstruiert)
- Textsorten
- Prüfliste
- Quellen

## Warum diese Datei auf Deutsch ist

Die Regeln für deutsche Texte stehen hier auf Deutsch, die übrigen Teile des Skills auf Englisch. Anthropic
rät, den Stil der Anweisung an den gewünschten Text anzupassen („Match your prompt style to the output you
want“). Ob deutsche Anweisungen zu idiomatischeren Entwürfen führen, ist nicht gemessen.
Das ist eine Annahme, kein Befund. Wer es prüfen will, lässt denselben Auftrag einmal mit dieser Datei und
einmal mit einer englischen Fassung schreiben und vergleicht die Treffer von `copy_lint.py --lang de`.

## Einordnung

- Kein einzelnes Merkmal beweist, dass ein Text maschinell entstanden ist. Die deutsche Wikipedia schreibt,
  dass nicht jeder Text mit den genannten Anzeichen KI-generiert ist und Detektoren als Beweis nicht reichen
  (https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte, geprüft 2026-11-01).
- Deutsche Listen von „KI-Wörtern“ sind dünne Belege: meist übersetzte englische Befunde oder redaktionelle
  Eindrücke. Eine Studie zu übermäßigem LLM-Vokabular im Deutschen gibt es nicht (Recherche 2026-11-03). Belegt
  ist etwas anderes: Ein Klassifikator hielt 60,2 % der deutschen Texte eines Modells und 37,6 % eines anderen
  für übersetzt, und die Leserinnen und Leser, denen es auffiel, nannten vor allem „ungewöhnliche Wörter oder
  Wortverbindungen“ (Valentini et al., COLM 2026).
- Daraus folgt: Die starken Regeln sind Typografie, Grammatik und Wortverbindungen. Wortlisten sind Hinweise.
- Fachwörter einer Branche sind keine Warnzeichen. „Zuverlässig“ in einer Buchungssoftware ist ein Kernwort.
  Geprüft wird die Aussage daneben: „Zuverlässig“ ohne Zahl ist eine Hoffnung, „98 % der Erinnerungen kamen im
  März vor dem Termin an“ ist eine Aussage.
- Wortlisten (Floskeln, Einstiege, Bedeutungsformeln, Lehnübersetzungen) liegen in `scripts/copy_lint.py`, nicht
  in dieser Datei. Wer eine verbotene Formulierung beim Schreiben liest, schreibt sie eher (Rana, arXiv
  2601.08070, an einem Modell gemessen). Der Linter läuft nach dem Entwurf.

## Anrede: du, Sie und Rechtstexte

[default] **du** für Oberfläche, Mails, Website und Support bei Software für Selbstbedienung, kleine Firmen,
Entwickler und Kreative. Rechtstexte (AGB, Datenschutzerklärung, AVV) dürfen beim Sie oder in der dritten Person
(„der Kunde“) bleiben, auf eigenen Seiten. Innerhalb einer Fläche wird nie gemischt. **Sie** für Zielgruppen in
Konzern-IT und Einkauf, Steuer und Lohn, Zahlungsinfrastruktur oder öffentlicher Verwaltung nur mit einer ADR,
die den Preis nennt: Sie klingt dort vertraut und korrekt, wirkt bei kleinen Teams aber steif und distanziert,
und ein späterer Wechsel betrifft jeden Text.

Was die Praxis zeigt (Live-Seiten, ausgezählt am 2026-11-03 in der Recherche, nur die überwiegende Form zählt):

| Form | Beispiele |
|---|---|
| du | Slack, Notion, Figma, Atlassian, Shopify, Lexware Office, sevDesk, Hetzner Cloud, Apple, Google Store, PayPal, N26, IKEA, Zalando |
| Sie | Microsoft, Google Workspace, Stripe, HubSpot, SAP, DATEV, IONOS, ELSTER |
| du im Produkt, Sie oder dritte Person im Recht | Shopify AGB, Lexware Office AGB und Datenschutz, Zalando Datenschutz, Apple Datenschutz, sevDesk AGB („Kunde“) |
| gemischt auf einer Seite (der eigentliche Fehler) | GitHub Docs („Beginnen Sie Ihre Reise“ neben „Festlegen deines Benutzernamens“), Mailchimp |

Manche Marken trennen nach Zielgruppe, nicht nach Satz: sevDesk spricht Unternehmer mit du an und
Steuerberater mit Sie, Google den Store mit du und Workspace mit Sie. Das ist eine Entscheidung pro Zielgruppe,
festgehalten in `voice.md`.

Schreibweise:
- „du“, „dich“, „dir“, „dein“ werden kleingeschrieben. In Briefen, also auch in Mails, darf großgeschrieben
  werden (Duden D 83; Rechtschreibrat § 66). Ein großes „Du“ auf Website und Oberfläche ist deshalb falsch
  (ADR02). Ob Mails „Du“ großschreiben, steht einmal in `voice.md` und gilt dann für alle Mails.
- „Sie“ und „Ihr“ als Anrede immer groß (Rechtschreibrat § 65).
- Buttons und Menüpunkte brauchen meist gar keine Anrede: „Link kopieren“, nicht „Kopiere deinen Link“.
- Der German-UPA-Leitfaden zum UX-Writing nennt „Duzen und Siezen vermischt“ als Negativbeispiel und
  „Konsequentes Duzen“ als Gegenstück.

## Der muttersprachliche Durchgang

Nach dem Entwurf kommt ein eigener Durchgang, der nur den deutschen Text liest, ohne englische Vorlage
daneben. Frage für jeden Satz: Würde eine deutsche Autorin diesen Satz schreiben, wenn es keine englische
Fassung gäbe? Wenn nein, wird der Satz neu geschrieben, nicht ausgebessert.

Warum ein eigener Durchgang: Eine Anweisung wie „schreib natürlich“ im Auftrag hat in einer Studie nichts
bewirkt (GPT-4, Anteil übersetzt wirkender Ausgaben 0,50 gegen 0,53). Ein Durchgang, in dem das Modell den
fertigen Text selbst überarbeitet, senkte den Anteil von 43 % auf 25 % (Li et al., arXiv 2503.04369). Die
Aufgabe wirkt, nicht die Stilvorgabe.

Worauf der Durchgang achtet:

| Muster | Erkennen | Umschreiben |
|---|---|---|
| Nominalstil | mehrere Substantive auf -ung, -keit, -ion in einem Satz, Verb am Ende ist „erfolgen“, „durchführen“, „vornehmen“ | „Die Speicherung erfolgt automatisch“ → „Wir speichern automatisch“ |
| Funktionsverbgefüge | „zur Verfügung stellen“, „in Kenntnis setzen“, „einer Prüfung unterziehen“, „Unterstützung bieten“ | „bereitstellen“, „informieren“, „prüfen“, „unterstützen“ (FVG01) |
| Lehnübersetzungen und Wortverbindungen | „eine Entscheidung machen“, „ein Problem adressieren“, „nicht länger verfügbar“, „in 2026“ | Liste mit Korpuszahlen in der Referenz zu Wortverbindungen (CAL01) |
| Genitivketten | drei Genitive hintereinander: „die Prüfung der Einstellungen des Kontos des Kunden“ | auflösen: „Prüf die Kontoeinstellungen des Kunden“ |
| Englische Wortstellung | Nebensatz vor dem Hauptsatz, wo Deutsch das Wichtige zuerst sagt; Partizip-Einschub („Mit einem Klick erstellt, ist die Rechnung ...“) | Hauptsatz zuerst, ein Gedanke pro Satz |
| Falsche Präpositionen | „für mehrere Minuten“, „auf der Seite“ für „auf die Seite“, „in 2026“, „über“ für „about“ („Infos über“ statt „zu“) | „mehrere Minuten lang“, „2026“, „Infos zu“ |
| Falsche Freunde | „eventuell“ für „eventually“, „aktuell“ für „actually“, „Billion“ für „billion“ | „schließlich“, „eigentlich“, „Milliarde“ |
| Possessiv-Häufung | „Verwalte deine Termine in deinem Kalender mit deinen Einstellungen“ | ein Possessiv reicht oder keins: „Termine im Kalender verwalten“ |
| Übersetztes Englisch im Ganzen | Satz, der sich Wort für Wort zurück ins Englische übersetzen lässt | vom Sachverhalt aus neu schreiben |

Danach `copy_lint.py --lang de` laufen lassen. Ein CAL01-Treffer heißt: Die Verbindung ist im Korpus selten,
die Alternative steht in der Meldung. Ein CAL02-Treffer ist ein Hinweis zum Register („Sinn machen“ ist laut
Duden umgangssprachlich, in Doku und Recht „ergibt Sinn“), kein Fehler.

## Typografie und Zeichensetzung

Diese Regeln beruhen auf Rechtschreibung und Stilnormen und gelten für jeden Text. Treffer haben die Codes TYP,
DSH und TTL.

- Gedankenstrich: Halbgeviertstrich mit Leerzeichen („ – “). Der Microsoft-Styleguide für Deutsch verwendet den
  Geviertstrich nicht; die deutsche Wikipedia nennt ihn im Fließtext ungewöhnlich. Bereiche ohne Leerzeichen:
  „37–39“. Der Linter meldet jeden Geviertstrich (DSH01).
- Strich mit Komma: Hausregel, keine Rechtschreibregel. Das Regelwerk erlaubt „Er weigert sich – leider –, nach
  Frankfurt zu kommen“, und DIN 5008 zeigt die Form als korrekt. In Produkttexten wird der Einschub trotzdem ein
  eigener Satz, weil der Satz sonst bricht (DSH02, DSH03). Prüfer nennen es nicht „Rechtschreibfehler“.
- Anführungszeichen: „…“ oder »…«, einheitlich; nie “…” (TYP01). Für Oberflächenbegriffe hilft Fettdruck in der
  genauen Schreibweise.
- Überschriften: erstes Wort und Substantive groß, keine englische Titelschreibung (Rechtschreibrat § 53;
  Microsoft 4.2.4, gilt auch für Softwaretexte). Der Linter findet großgeschriebene Funktionswörter (TTL01),
  großgeschriebene Adjektive findet nur ein Mensch.
- Apostroph: kein Apostroph vor dem Genitiv-s („Annas Projekt“) und im Plural („die APIs“). Ausnahmen nach s, ß,
  x, z (§ 80), deshalb meldet TYP02 nur zur Prüfung.
- Zusammensetzungen: ein Wort oder mit Bindestrich, nie getrennt: „Rechnungsnummer“, „E-Mail-Adresse“,
  „KI-Funktion“ (TYP03).
- Kein Satzzeichen direkt hinter einer Beschriftung, die auf ? ! … endet (TYP04).
- Zahlen und Geld: Dezimalkomma, Betrag vor dem Währungszeichen mit Leerzeichen: „19 €“, „1.234,50 €“ (TYP05).
  Bei Anzahlen gruppiert DIN 5008 mit Leerzeichen („1 500“), Microsoft mit Punkt („1.500“). Das ist eine
  Hausentscheidung und steht einmal in `voice.md`.
- Datum und Uhrzeit nach DIN 5008: „03.11.2026“ oder „2026-11-03“, „14:30 Uhr“, „8 Uhr“.

## Satzbau und Grammatik

- Verben statt Substantivketten, Aktiv mit benannter Person: „Seitens des Systems wird eine Benachrichtigung
  versendet“ wird „Wir schicken dir eine Nachricht“. Nicht mehr als vier Substantive in Folge (Leitfaden
  Bürgernahe Sprache, Brandenburg).
- „wir“ für die Firma, „du“ oder „Sie“ für die Leserin; „man“ nicht in Anleitungen.
- Höchstens 25 Wörter pro Satz, besser um 15. Hauptsatz zuerst, kein Nebensatz in der Mitte eingeschoben
  (LEN01 meldet mehr als 15 % Sätze über 25 Wörter).
- Indikativ und Imperativ statt Konjunktiv („Du kannst ...“, nicht „Du könntest ...“). Der Microsoft-Styleguide
  hält den Konjunktiv für seinen Stil für ungeeignet.
- Ein Satz, ein Gedanke. Das Substantiv wiederholen, wenn ein Pronomen auf zwei Dinge zeigen könnte.
- Zeitform: Produkttext im Präsens; Changelog im Präsens oder Perfekt, durchgehend gleich.
- „Darüber hinaus“, „Zudem“, „Außerdem“ am Satzanfang höchstens etwa einmal pro 150 Wörter (CON01; Schwelle ist
  eine Gestaltungsentscheidung dieses Skills).
- Superlative brauchen eine Grundlage im selben Satz (SUP01). Doppelte Superlative („optimalste“, „einzigste“)
  sind in jedem Register falsch.

## Begriffe, Anglizismen, Gendern

- Ein Begriff pro Sache, festgehalten im Glossar der Voice-Dateien. Der German-UPA-Leitfaden: „Prüfe, ob es eine
  Terminologie-Datenbank gibt. Wenn ja, nutze sie.“
- Englische Begriffe nur, wenn sie das Standardwort der Zielgruppe sind oder so in der Oberfläche stehen. Der
  Microsoft-Styleguide: nur „if they are indeed the industry standard in Germany“, und das ersetzt keine
  Recherche. Englische Verben werden deutsch gebeugt („wir mailen“, „gelikt“ oder „geliked“).
- Deutsche Grammatik um englische Namen: „die Agent Tools von xAI“, nicht „xAI's Agent Tools“.
- Gendern: ein Ansatz pro Produkt. Der Microsoft-Styleguide (mit Microsoft Deutschland abgestimmt) empfiehlt,
  das generische Maskulinum zu verringern statt ganz zu streichen, zuerst neutrale Wörter und Plural-Partizipien
  („Teilnehmende“), Genderstern und ähnliche Zeichen nicht, weil sie Lesbarkeit und Bedienbarkeit
  beeinträchtigen können. Der Rechtschreibrat zählt wortinterne Zeichen nicht zum Kernbestand der
  Rechtschreibung (Regelwerk 2024). Sichtbarer Fehler ist die Mischung („Kund:innen“ neben „Kunden“).

## Umschreibbeispiele (konstruiert)

Alle Paare sind für diesen Skill gebaut, keine freigegebenen Produkttexte. Werte in geschweiften Klammern stehen
für echte, belegte Werte.

Startseite, Rechnungsprogramm

- Entwurf: „In der heutigen schnelllebigen Welt ist eine gute Buchhaltung nicht nur ein Nice-to-have, sie ist
  ein echter Mehrwert. Tauche ein in eine Welt ohne offene Posten.“
- Neu: „Du schreibst die Rechnung, wir schicken sie als PDF und erinnern deinen Kunden nach {14} Tagen, wenn
  er nicht gezahlt hat.“
- Geändert: Einstieg, Gegensatz, Floskel und Lehnübersetzung sind weg; was passiert und wann, steht da; du
  durchgehend.

Nominalstil, Buchungssoftware

- Entwurf: „Die Durchführung der Versendung der Terminerinnerungen erfolgt seitens des Systems 24 Stunden vor
  dem Termin.“
- Neu: „Deine Gäste bekommen 24 Stunden vor dem Termin eine Erinnerung.“
- Geändert: Verb trägt die Handlung, die Person ist genannt, ein Gedanke.

Übersetzte Wortverbindungen, Projekttool

- Entwurf: „Wir sind aufgeregt, euch das neue Board zu zeigen. Es adressiert das Problem, dass Aufgaben nicht
  länger sichtbar waren, und hilft euch, bessere Entscheidungen zu machen.“
- Neu: „Das neue Board zeigt alle offenen Aufgaben eines Projekts auf einer Seite, auch die erledigten der
  letzten {7} Tage.“
- Geändert: „Wir sind aufgeregt“ (1 : 745), „adressieren“ (1 : 130), „Entscheidungen machen“ (1 : 138) sind
  weg; statt eines Nutzens steht da, was das Board zeigt.

Typografie

- Entwurf: „Die "Online Rechnung" zeigt Kunden's Zahlungen. Das kostet €19 pro Monat. In 2026 haben wir 1,000
  Rechnungen pro Tag verschickt.“
- Neu: „Die Online-Rechnung zeigt die Zahlungen deiner Kunden. Das kostet 19 € im Monat. 2026 haben wir
  1.000 Rechnungen pro Tag verschickt.“
- Geändert: Zusammensetzung verbunden, kein Apostroph, deutsches Zahlen- und Preisformat, kein „in 2026“. (Die
  Zahl braucht in echtem Text eine Quelle.)

Einschub mit Strichen

- Entwurf: „Wer Termine aus der eigenen Website heraus bucht – etwa über das Buchungs-Widget –, muss dafür
  kein Konto anlegen.“
- Neu: „Gäste buchen direkt über das Widget auf deiner Website. Ein Konto brauchen sie dafür nicht.“
- Geändert: Einschub wird eigener Satz; aktiv; zwei klare Aussagen.

## Textsorten

Die Registertabelle, die Referenz zu UI-Texten und die Referenz zu Transaktionsmails gelten für beide
Sprachen. Für Deutsch kommt hinzu:

- Startseite: erster Satz sagt, was das Produkt tut und für wen, im Hauptsatz. Überschriften in deutscher
  Satzschreibung, nicht „X: Y“. Buttons Verb plus Objekt („Rechnung schreiben“), nicht „Mehr erfahren“ allein
  (CTA01). Preise als „19 € im Monat“; bei Geschäftskunden einmal „alle Preise zzgl. MwSt.“ oder „netto“.
- Feature-Seite: pro Funktion was sie tut, ein konkretes Beispiel oder eine Zahl, wo man sie findet. Den echten
  Umfang nennen statt „Egal ob ...“.
- Changelog: Präsens oder Perfekt, durchgehend. Pro Eintrag Objekt, Änderung, was die Leserin jetzt tun kann.
  Nur, was Kunden sehen oder nutzen. Gruppen wie in Keep a Changelog: Hinzugefügt, Geändert, Veraltet, Entfernt,
  Behoben, Sicherheit.
- Mail: Betreff sagt, was drinsteht, in Satzschreibung. Erste Zeile bringt die Nachricht. Gruß ohne Komma
  („Viele Grüße“). Dieselbe Anrede wie im Produkt.
- Doku: Imperativ, ein Schritt pro Zeile, Oberflächenbegriffe fett. Keine Werbewörter, kein „einfach“, kein
  „bitte“ als Füllwort. Abkürzungen beim ersten Mal erklären.

## Prüfliste

- Jede Zahl, jeder Kunde, jedes Zitat, jeder Superlativ hat eine Quelle oder `{TODO: source}`.
- Eine Anrede auf der ganzen Fläche; du klein (außer in Mails nach Hausregel), Sie groß.
- Muttersprachlicher Durchgang gemacht: kein Satz, der nur mit englischer Vorlage so entstünde.
- Keine Lehnübersetzung aus der Liste, kein Funktionsverbgefüge ohne Grund, keine Genitivkette.
- „…“, Halbgeviertstrich mit Leerzeichen, kein Geviertstrich, kein Strich mit Komma, kein Apostroph-s,
  Zusammensetzungen verbunden, „19 €“, Dezimalkomma.
- Überschriften in Satzschreibung, ohne Emoji.
- Ein Begriff pro Sache nach Glossar; Markennamen so, wie die Marke sie schreibt; ein Gender-Ansatz.
- Nichts Ungebautes, nichts Internes.
- Laut gelesen.

## Quellen

- https://arxiv.org/html/2608.17399: Valentini et al., übersetzt wirkendes Deutsch in LLM-Texten, 60,2 % und
  37,6 % (geprüft 2026-11-03 in der Recherche).
- https://arxiv.org/html/2503.04369: Li et al., Stilvorgabe ohne Wirkung, Überarbeitung 43 % auf 25 % (geprüft
  2026-11-03 in der Recherche).
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices:
  Stil der Anweisung an den Zieltext anpassen (geprüft 2026-11-03 in der Recherche).
- https://www.duden.de/sprachwissen/rechtschreibregeln/gross-und-kleinschreibung: D 83, du klein, in Briefen
  groß erlaubt (geprüft 2026-11-03).
- https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf: §§ 53, 65, 66, 80 (geprüft 2026-11-01).
- https://aka.ms/german-styleguide: Gedankenstrich, Anführungszeichen, Überschriften, Anglizismen, Konjunktiv,
  Gendern (geprüft 2026-11-01 und 2026-11-03).
- https://germanupa.de/sites/default/files/2024-05/leitfaden_ux-writing_heuristiken_v1.01_0.pdf: Heuristik 6,
  Terminologie, du/Sie gemischt als Negativbeispiel (geprüft 2026-11-03 in der Recherche).
- https://mik.brandenburg.de/sixcms/media.php/9/BuergernaheSpracheinderVerwaltung.pdf: Verben statt
  Substantive, Aktiv, höchstens vier Substantive in Folge (geprüft 2026-11-01).
- https://www.uni-passau.de/fileadmin/dokumente/beschaeftigte/kommunikation_marketing/webredaktion/DIN_5008.pdf:
  DIN 5008, Datum, Uhrzeit, Zahlen (geprüft 2026-11-03 in der Recherche).
- https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte: Anzeichen sind kein Beweis
  (geprüft 2026-11-01).
- https://t3n.de/news/du-marketing-hoeflichkeit-1392659/: mehr Firmen duzen, IKEA, Apple, Aldi (geprüft
  2026-11-03 in der Recherche).
