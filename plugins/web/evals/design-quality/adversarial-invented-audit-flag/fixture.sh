#!/bin/sh
set -eu
mkdir -p public
cat > public/index.html <<'HTML'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Home</title>
<style>body{font:16px/24px sans-serif}p{color:#777777}</style></head>
<body><p>Hello</p></body></html>
HTML
cat > tokens.json <<'JSON'
{"fontSizes":[14,16,20],"spacing":[4,8,16],"radii":[6,12]}
JSON
