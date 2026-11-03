#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy
cat > copy/fakten.md <<'MD'
# Fakten (von der Produktverantwortlichen bestätigt)

Produkt: Projekttool für kleine Agenturen. Anrede: du, überall. Der Begriff heißt "Aufgabe", nie "Task".

Fehlerfall beim Speichern einer Aufgabe:
- Tritt auf, wenn keine Internetverbindung besteht.
- Der Entwurf bleibt auf dem Gerät erhalten, nichts geht verloren.
- Das Tool versucht alle 30 Sekunden erneut zu speichern, sobald wieder eine Verbindung da ist.
- Die Nutzerin muss nichts tun. Sie kann weiterarbeiten.

Leerzustand der Aufgabenliste:
- Erscheint in einem Projekt ohne Aufgaben.
- Die einzige Aktion ist der Button "Aufgabe anlegen" (so heißt er in der Oberfläche).
MD
cat > copy/ui-texte.md <<'MD'
## Fehlermeldung

Ups! Leider ist beim Speichern Ihres Tasks ein Fehler aufgetreten. Die Speicherung konnte nicht durchgeführt werden. Bitte versuchen Sie es zu einem späteren Zeitpunkt erneut!

## Leerzustand

Hier ist es noch ganz schön leer! Starte jetzt durch und kreiere deinen ersten Task, um das volle Potenzial deines Projekts freizuschalten.

Mehr erfahren
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add ui text draft'
