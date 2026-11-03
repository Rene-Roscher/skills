#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/product leads
cat > docs/product/brief.md <<'MD'
# Product brief: project tool for small agencies

Buyer: owner of a design or web agency with 5 to 30 people in Germany and Austria.
Alternative today: spreadsheets plus a time-tracking app.
Positioning: client projects, hours and invoices in one tool.
MD
cat > leads/agencies.csv <<'CSV'
company,city,contact_name,email
Pixelwerk GmbH,Hamburg,A. Example,owner@pixelwerk.example.com
Studio Nord UG,Kiel,B. Example,hello@studionord.example.com
Formfabrik GmbH,Leipzig,C. Example,info@formfabrik.example.com
CSV
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add brief and lead list'
