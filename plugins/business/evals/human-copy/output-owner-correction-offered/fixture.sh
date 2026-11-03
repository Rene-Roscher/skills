#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy docs/voice/examples
cat > docs/voice/voice.md <<'MD'
# Voice: booking system for physiotherapy practices

Owner: head of product · Last reviewed: 2026-10-20

## Address form

- German: du in product UI, mails, website and support. du/dein lowercase.
- Legal texts: Sie, on their own pages.

## Tone per surface

| Surface | Tone in one line |
|---|---|
| Transactional mail | friendly, plain, the booked time in the first line |
MD
cat > docs/voice/glossary.md <<'MD'
# Glossary

| lang | preferred | avoid | note |
|---|---|---|---|
| de | Praxis | Studio | |
MD
cat > docs/voice/corrections.jsonl <<'JSONL'
{"date": "2026-10-28", "surface": "button", "lang": "de", "before": "Slot wählen", "after": "Termin wählen", "reason": "Wir sagen Termin, nicht Slot", "class": "terminology", "rule": "Termin statt Slot", "promoted": ""}
JSONL
cat > copy/buchung.md <<'MD'
# Buchungsbestätigung (Mail)

Betreff: Dein Termin am 12. November um 14:30 Uhr ist bestätigt

Hallo Anna,

dein Slot am 12. November um 14:30 Uhr in der Praxis Lindner ist gebucht.

Wenn du nicht kannst, verschiebe den Slot bis 24 Stunden vorher über den Link unten.

Viele Grüße
Praxis Lindner
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add booking mail draft'
