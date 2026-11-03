#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p site
for page in index features pricing; do
cat > "site/$page.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<title>Project tool for small agencies - $page</title>
<link rel="canonical" href="https://www.example.com/$page">
</head>
<body>
<h1>Plan client projects without spreadsheets</h1>
<p>Track tasks, hours and invoices for every client project in one place.</p>
<section id="faq">
<h2>Questions</h2>
<h3>Can I import from a spreadsheet?</h3>
<p>Yes. Upload a CSV with one row per task.</p>
</section>
</body>
</html>
HTML
done
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add site pages'
