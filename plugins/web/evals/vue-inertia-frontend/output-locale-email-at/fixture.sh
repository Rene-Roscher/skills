#!/bin/sh
set -eu
mkdir -p resources/js/locales/en
cat > package.json <<'JSON'
{ "private": true, "dependencies": { "vue": "^3.5.0", "vue-i18n": "^11.0.0", "@inertiajs/vue3": "^2.1.0" } }
JSON
cat > resources/js/locales/en/support.json <<'JSON'
{
  "support": {
    "title": "Support"
  }
}
JSON
