---
type: llm
weight: 3
focus:
  source: file
  path: copy/ui-texte.md
---

Judge only the German UI text in the file, as a native German UX editor would.

PASS if all of these hold: the error message says what happened (the task was not saved because there is no connection) and what happens next (the draft stays on the device, saving is retried every 30 seconds) in at most three short sentences; the empty state says what will appear there and offers exactly one action, the button "Aufgabe anlegen"; the reader is addressed with lowercase du throughout; every sentence is one a German writer would produce without an English source.

FAIL if any of these appear: apology or cheer ("Ups", "Hoppla", "leider", "Sorry", "Super", "ganz schön leer"); "bitte" or an exclamation mark in the error; Sie or Ihr anywhere; nominal style or Funktionsverbgefüge ("Speicherung", "durchführen", "erfolgen", "zur Verfügung stellen"); calques or English word combinations ("nicht länger", "eine Entscheidung machen", "kreieren", "Potenzial freischalten", "Starte durch"); the English word "Task"; a generic "Ein Fehler ist aufgetreten" without naming what failed; a claim the facts file does not contain (for example that nothing can ever be lost, or a support contact); more than one action in the empty state.
