#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy
cat > copy/fakten.md <<'EOF'
# Fakten zum Produkt (vom Produktverantwortlichen bestätigt)

- Prüfintervall ab 30 Sekunden, pro Prüfung einstellbar. Standard sind 60 Sekunden.
- Geprüft wird von vier Standorten aus.
- Bei Ausfall: Benachrichtigung per SMS, Anruf oder E-Mail.
- Einrichtung: Es genügt die Adresse der Website.
- Das Produkt spricht alle Nutzer mit "du" an (Oberfläche, Mails, Doku).
- Preis: 19 € im Monat, netto.
EOF
cat > copy/startseite.md <<'EOF'
# Schnelle Und Zuverlässige Überwachung Für Deine Websites

In der heutigen schnelllebigen Welt ist zuverlässiges Monitoring nicht nur ein Nice-to-have — es ist ein echter Gamechanger. Egal ob Startup oder Enterprise: Unsere ganzheitliche Plattform bietet Ihnen eine nahtlose Integration in deine bestehenden Workflows. Tauche ein in eine Welt, in der Ausfälle der Vergangenheit angehören. Darüber hinaus wird durch die Bereitstellung von maßgeschneiderten Dashboards ein echter Mehrwert für Ihr Team geschaffen. Das kostet €19 pro Monat.

Mehr erfahren
EOF
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add startseite draft'
